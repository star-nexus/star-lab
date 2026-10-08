// Included in a diagnostic copy of the pinned PyO3 boundary, never the wheel.
#[cfg(test)]
mod e8_faults {
    use super::*;
    fn make(py: Python<'_>) -> NativeRuntime {
        NativeRuntime::new(py, include_str!("../initial.json").into(), 1).unwrap()
    }
    fn request(action: &str, parameters: Value, wall: f64) -> String {
        json!({"agent_id":"alpha", "action":action, "parameters":parameters,
            "wall_time":wall}).to_string()
    }
    fn query(wall: f64) -> String { request("get_faction_state", json!({"faction":"wei"}), wall) }
    fn compare(a: &NativeRuntime, b: &NativeRuntime) {
        let a = a.inner.lock().unwrap(); let b = b.inner.lock().unwrap();
        let a = a.runtime.as_ref().unwrap(); let b = b.runtime.as_ref().unwrap();
        assert_eq!(serde_json::to_value(a.export()).unwrap(), serde_json::to_value(b.export()).unwrap());
        assert_eq!(a.admitted_query_accounting_snapshot(Some("alpha")), b.admitted_query_accounting_snapshot(Some("alpha")));
    }
    #[test]
    fn exhausted_revision_preserves_release_prefix_and_invalidates() {
        Python::initialize(); Python::attach(|py| {
            let a=make(py); let b=make(py);
            let token=b._begin_observation_segment_json(py,"segment_encoded".into(),4,true).unwrap().unwrap();
            assert_eq!(a.execute_action_json(py,query(1.)).unwrap(),b._observation_segment_request_json(py,token.clone(),query(1.)).unwrap());
            for n in [&a,&b] { n.inner.lock().unwrap().runtime.as_mut().unwrap().revision=u64::MAX; }
            let unit: u64=37; // Frozen tiny fixture alpha claim.
            let bad=request("release_units",json!({"unit_ids":[unit,[1]]}),2.);
            for n in [&a,&b] { assert!(n.execute_action_json(py,bad.clone()).unwrap_err().to_string().contains("revision exhausted")); }
            assert!(b.inner.lock().unwrap().segment.is_none()); compare(&a,&b);
            let state=serde_json::to_value(a.inner.lock().unwrap().runtime.as_ref().unwrap().export()).unwrap();
            assert_eq!(state["singletons"]["TeamCoordination"]["unit_owners"],json!({}));
            assert_eq!(a.execute_action_json(py,query(3.)).unwrap(),b._observation_segment_request_json(py,token,query(3.)).unwrap());
            compare(&a,&b); a.close(py).unwrap(); b.close(py).unwrap();
        });
    }
    #[test]
    fn final_encoding_failure_preserves_commit_without_cache_or_retry() {
        Python::initialize(); Python::attach(|py| {
            let a=make(py); let b=make(py);
            let token=b._begin_observation_segment_json(py,"segment_encoded".into(),4,true).unwrap().unwrap();
            let owned=b._observation_segment_request_json(py,token.clone(),query(1.)).unwrap();
            assert_eq!(a.execute_action_json(py,query(1.)).unwrap(),owned);
            E8_FAIL_ENCODING.with(|fault| fault.set(true));
            assert!(a.execute_action_json(py,query(2.)).unwrap_err().to_string().contains("injected final encode fault"));
            E8_FAIL_ENCODING.with(|fault| fault.set(true));
            assert!(b._observation_segment_request_json(py,token.clone(),query(2.)).unwrap_err().to_string().contains("injected final encode fault"));
            assert!(b.inner.lock().unwrap().segment.is_none()); compare(&a,&b);
            assert_eq!(a.inner.lock().unwrap().runtime.as_ref().unwrap().admitted_query_accounting_snapshot(Some("alpha"))["agent_actions"],json!(2));
            let fresh=b._begin_observation_segment_json(py,"segment_encoded".into(),4,true).unwrap().unwrap();
            assert_eq!(a.execute_action_json(py,query(3.)).unwrap(),b._observation_segment_request_json(py,fresh.clone(),query(3.)).unwrap());
            let report: Value=serde_json::from_str(&b._end_observation_segment_json(py,fresh).unwrap().unwrap()).unwrap();
            assert_eq!(report["query_diagnostics"][0]["metrics"]["census_builds"],json!(1));
            assert_eq!(report["requests"],json!(1)); compare(&a,&b);
            a.close(py).unwrap(); b.close(py).unwrap();
            assert!(serde_json::from_str::<Value>(&owned).unwrap()["success"].as_bool().unwrap());
        });
    }
    #[test]
    fn generation_exhaustion_disables_cache_but_ordinary_request_survives() {
        Python::initialize(); Python::attach(|py| {
            let n=make(py); n.inner.lock().unwrap().generation=u64::MAX;
            assert!(n._begin_observation_segment_json(py,"segment_encoded".into(),4,true).unwrap_err().to_string().contains("generation exhausted"));
            assert!(n.inner.lock().unwrap().segment.is_none());
            assert!(serde_json::from_str::<Value>(&n.execute_action_json(py,query(1.)).unwrap()).unwrap()["success"].as_bool().unwrap());
            assert_eq!(n.inner.lock().unwrap().generation,u64::MAX);n.close(py).unwrap();
        });
    }
    #[test]
    fn repeated_segments_and_reset_keep_only_current_cache() {
        Python::initialize(); Python::attach(|py| {
            let n=make(py);let mut expected=None;
            for cycle in 0..64 {
                if cycle>0 && cycle%8==0 { n.reset(py,include_str!("../initial.json").into()).unwrap(); }
                let token=n._begin_observation_segment_json(py,"segment_encoded".into(),4,true).unwrap().unwrap();
                for i in 0..4 { n._observation_segment_request_json(py,token.clone(),query((cycle*4+i) as f64)).unwrap(); }
                let report: Value=serde_json::from_str(&n._end_observation_segment_json(py,token).unwrap().unwrap()).unwrap();
                assert_eq!(report["requests"],json!(4));
                assert_eq!(report["query_diagnostics"][0]["metrics"]["census_builds"],json!(1));
                for i in 1..4 { assert_eq!(report["query_diagnostics"][i]["metrics"]["census_builds"],json!(0)); }
                let summary=report["cache_before_drop"].clone();
                if let Some(ref old)=expected { assert_eq!(&summary,old); } else { expected=Some(summary); }
                assert!(n.inner.lock().unwrap().segment.is_none());
            }
            n.close(py).unwrap();let state=n.inner.lock().unwrap();
            assert!(state.segment.is_none() && state.runtime.is_none());
        });
    }
}
