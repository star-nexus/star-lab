//! Mechanism-only feasibility probe using locked Bevy and production components.
//! These small systems are not substitutes for the production advance_* methods.
use bevy_ecs::{batching::BatchingStrategy, entity::EntityHashSet, prelude::*,
    schedule::{MultiThreadedExecutor, SingleThreadedExecutor}};
use bevy_tasks::{ComputeTaskPool, TaskPoolBuilder};
use serde_json::json;
use star_core::{read_pool::ReadPool, world::OrderedWorld};
use star_rotk::{components::MovePoints, vision::Vision};
use std::{collections::HashSet, sync::{Mutex, atomic::{AtomicUsize, Ordering}}, time::{Duration, Instant}};

#[derive(Resource)]
struct Gate {
    active: AtomicUsize,
    maximum: AtomicUsize,
    arrived: AtomicUsize,
    rendezvous: bool,
    threads: Mutex<HashSet<std::thread::ThreadId>>,
}
impl Gate {
    fn new(rendezvous: bool) -> Self {
        Self { active: AtomicUsize::new(0), maximum: AtomicUsize::new(0),
            arrived: AtomicUsize::new(0), rendezvous, threads: Mutex::new(HashSet::new()) }
    }
    fn enter(&self) {
        self.threads.lock().unwrap().insert(std::thread::current().id());
        let active = self.active.fetch_add(1, Ordering::SeqCst) + 1;
        self.maximum.fetch_max(active, Ordering::SeqCst);
        self.arrived.fetch_add(1, Ordering::SeqCst);
        if self.rendezvous {
            let deadline = Instant::now() + Duration::from_secs(2);
            while self.arrived.load(Ordering::SeqCst) < 2 {
                assert!(Instant::now() < deadline, "independent systems did not overlap");
                std::thread::yield_now();
            }
        }
        // Deliberately hold a synthetic work window to observe overlap. Not timed.
        std::thread::sleep(Duration::from_millis(2));
    }
    fn leave(&self) { self.active.fetch_sub(1, Ordering::SeqCst); }
}
fn mp(mut q: Query<&mut MovePoints>, gate: Res<Gate>) {
    gate.enter();
    for mut value in &mut q { value.current_mp += 1; }
    gate.leave();
}
fn mp_second(mut q: Query<&mut MovePoints>, gate: Res<Gate>) {
    gate.enter();
    for mut value in &mut q { value.current_mp += 1; }
    gate.leave();
}
fn vision(mut q: Query<&mut Vision>, gate: Res<Gate>) {
    gate.enter();
    for mut value in &mut q { value.dirty = false; }
    gate.leave();
}
#[derive(Resource, Default)]
struct Monolith { first: usize, second: usize }
fn monolith_a(mut value: ResMut<Monolith>, gate: Res<Gate>) {
    gate.enter(); value.first += 1; gate.leave();
}
fn monolith_b(mut value: ResMut<Monolith>, gate: Res<Gate>) {
    gate.enter(); value.second += 1; gate.leave();
}
fn exclusive(world: &mut World) {
    let gate = world.resource::<Gate>(); gate.enter(); gate.leave();
}
fn new_world(rendezvous: bool) -> World {
    let mut world = World::new();
    world.insert_resource(Gate::new(rendezvous));
    world.insert_resource(Monolith::default());
    world.spawn((MovePoints { current_mp: 0, max_mp: 6, base_mp: 6, has_moved: false },
        Vision { range: 3, visible_tiles: Default::default(), last_pos: None, last_range: 0, dirty: true }));
    world
}
fn run_schedule(threads: usize, case: &str) -> serde_json::Value {
    let independent = case == "disjoint_components";
    let mut world = new_world(independent && threads > 1);
    let mut schedule = Schedule::default();
    if threads == 1 { schedule.set_executor(SingleThreadedExecutor::new()); }
    else { schedule.set_executor(MultiThreadedExecutor::new()); }
    match case {
        "disjoint_components" => { schedule.add_systems((mp, vision)); },
        "same_component" => { schedule.add_systems((mp, mp_second)); },
        "same_resource_different_fields" => { schedule.add_systems((monolith_a, monolith_b)); },
        "exclusive_world" => { schedule.add_systems((exclusive, vision)); },
        _ => unreachable!(),
    }
    schedule.run(&mut world);
    let maximum = world.resource::<Gate>().maximum.load(Ordering::SeqCst);
    assert_eq!(maximum, if independent && threads > 1 { 2 } else { 1 });
    let mut query = world.query::<(&MovePoints, &Vision)>();
    let (points, sight) = query.single(&world).unwrap();
    if independent { assert_eq!(points.current_mp, 1); assert!(!sight.dirty); }
    if case == "same_component" { assert_eq!(points.current_mp, 2); }
    if case == "same_resource_different_fields" {
        assert_eq!((world.resource::<Monolith>().first, world.resource::<Monolith>().second), (1, 1));
    }
    json!({"case":case,"maximum_simultaneous_bodies":maximum,"passed":true})
}
#[derive(Resource)]
struct Active(EntityHashSet);
fn active_query(mut q: Query<&mut MovePoints>, active: Res<Active>) {
    q.par_iter_many_unique_mut(&active.0).batching_strategy(BatchingStrategy::fixed(8))
        .for_each(|mut value| { value.current_mp += 1; });
}
fn active_subset() -> serde_json::Value {
    let mut world = OrderedWorld::new(5001);
    let mut active = EntityHashSet::new();
    for id in 1..=5000 {
        let entity = world.import(id).unwrap();
        world.ecs.entity_mut(entity).insert(MovePoints { current_mp:0, max_mp:6, base_mp:6, has_moved:false });
        if id % 50 == 0 { active.insert(entity); }
    }
    world.ecs.insert_resource(Active(active));
    let mut schedule = Schedule::default();
    schedule.add_systems(active_query);
    schedule.run(&mut world.ecs);
    for (id, entity) in world.ordered() {
        assert_eq!(world.ecs.get::<MovePoints>(entity).unwrap().current_mp, i64::from(id % 50 == 0));
    }
    json!({"case":"internal_unique_active_query","resident":5000,"selected":100,"changed":100,"passed":true,
        "scope":"mechanism only; order and actual worker participation are not promised by par_iter"})
}
fn scoped_probe(threads: usize) -> serde_json::Value {
    let pool = ReadPool::new(threads);
    let input: Vec<u64> = (0..5000).collect();
    let serial: Vec<_> = input.iter().map(|id| id.wrapping_mul(17)).collect();
    let chunks = pool.map_chunks(&input, |ids| ids.iter().map(|id| id.wrapping_mul(17)).collect::<Vec<_>>());
    assert_eq!(chunks.into_iter().flat_map(|(rows, _)| rows).collect::<Vec<_>>(), serial);
    // Empty work with nonempty chunks isolates dispatch/join/result bookkeeping.
    let tiny: Vec<_> = (0..threads).collect();
    for _ in 0..100 { std::hint::black_box(pool.map_chunks(&tiny, |_| ())); }
    let samples: Vec<u64> = (0..1000).map(|_| {
        let start = Instant::now();
        std::hint::black_box(pool.map_chunks(&tiny, |_| ()));
        start.elapsed().as_nanos() as u64
    }).collect();
    let mut ordered = samples.clone(); ordered.sort_unstable();
    json!({"case":"existing_scoped_pool","threads":threads,"ordered_5000_outputs_equal":true,
        "dispatch_samples_ns":samples,"dispatch_median_ns":ordered[500],"dispatch_p99_ns":ordered[990],
        "passed":true,"scope":"empty job dispatch diagnostic; not System or frame speedup"})
}
fn main() {
    let args: Vec<_> = std::env::args().collect();
    let mode = &args[1]; let threads: usize = args[2].parse().unwrap();
    assert!(matches!(threads, 1 | 2 | 4));
    let report = if mode == "schedule" {
        ComputeTaskPool::get_or_init(|| TaskPoolBuilder::new().num_threads(threads).build());
        let checks: Vec<_> = ["disjoint_components", "same_component", "same_resource_different_fields", "exclusive_world"]
            .into_iter().map(|case| run_schedule(threads, case)).collect();
        json!({"mode":mode,"threads":threads,"checks":checks,"active_subset":active_subset(),"all_passed":true})
    } else {
        assert_eq!(mode, "scoped"); assert!(threads > 1);
        json!({"mode":mode,"threads":threads,"checks":[scoped_probe(threads)],"all_passed":true})
    };
    println!("{}", report);
}
