# P0 成本与缓存契约

各分项为独立带探针运行，inclusive包含子区间；self只扣除本探针捕获的直接嵌套区间。不能相加重叠inclusive或阶段P99。

## baseline

9880个完整tick，同一扩展。

| scope | calls | inclusive ms/tick | self ms/tick |
|---|---:|---:|---:|
| method.MapRenderSystem._render_territory_boundaries_optimized | 9880 | 2.370699 | 2.370699 |
| method.UIRenderSystem._current_faction_counts | 9880 | 1.030041 | 1.030041 |
| profile.render_scalar_execute | 2439535 | 1.083836 | 1.016933 |
| rms.draw | 3925361 | 0.871949 | 0.724922 |
| method.UnitRenderSystem._get_visible_units | 9880 | 0.720159 | 0.720159 |
| method.UnitRenderSystem._render_units_batch | 9880 | 3.085148 | 0.620838 |
| method.UnitRenderSystem._render_single_unit_fast | 3337364 | 1.737521 | 0.544423 |
| profile.render_queue_submit | 9880 | 1.899845 | 0.459305 |
| method.UnitRenderSystem._render_simple_health_bar | 703430 | 0.456602 | 0.387187 |
| method.UnitRenderSystem._render_unit_group_optimized | 3107767 | 2.077324 | 0.377954 |
| method.UnitRenderSystem._get_fast_animation_screen_position | 3337364 | 0.348834 | 0.348834 |
| profile.render_batch_blits | 491899 | 0.244894 | 0.244894 |
| method.EffectRenderSystem._render_attack_indicators | 9880 | 0.203087 | 0.202587 |
| method.UnitRenderSystem.update | 9880 | 3.961967 | 0.146976 |
| profile.render_batch_pack | 754098 | 0.111810 | 0.111810 |
| rms._add_command | 6082973 | 0.107121 | 0.107121 |
| method.PanelRenderSystem._render_battle_log | 9880 | 0.120922 | 0.095023 |
| method.MapRenderSystem._render_terrain_direct | 36 | 0.166103 | 0.085660 |
| construct.BlitCommand | 3925361 | 0.077053 | 0.077053 |
| method.EffectRenderSystem._render_attack_effects | 9880 | 0.083119 | 0.071588 |
| method.MapRenderSystem._render_fog_of_war_optimized | 9880 | 0.075851 | 0.069682 |
| sdl.draw.rect | 2139930 | 0.066720 | 0.066720 |
| method.MiniMapSystem._render_minimap | 9880 | 0.052416 | 0.041412 |
| construct.DrawCommand | 2157612 | 0.034134 | 0.034134 |
| method.UIRenderSystem._render_faction_status_indicators | 9880 | 1.064843 | 0.026408 |
| method.UIRenderSystem._render_real_time_info | 9880 | 1.090341 | 0.020747 |
| method.PanelRenderSystem._render_view_mode_info | 9880 | 0.026286 | 0.019599 |
| method.MapRenderSystem._get_terrain_texture | 342780 | 0.013193 | 0.013193 |
| method.UIRenderSystem._render_game_info | 9880 | 1.105809 | 0.012736 |
| method.MapRenderSystem.update | 9880 | 2.653350 | 0.012477 |
| method.EffectRenderSystem.update | 9880 | 0.312168 | 0.010481 |
| method.MapRenderSystem._render_map_optimized | 9880 | 0.192313 | 0.008430 |
| method.MapRenderSystem._draw_overscan | 9844 | 0.011890 | 0.006625 |
| method.MiniMapSystem._render_camera_viewport | 9880 | 0.007333 | 0.006234 |
| method.EffectRenderSystem._render_slash_effect | 7142 | 0.007947 | 0.004946 |
| method.PanelRenderSystem.update | 9880 | 0.152347 | 0.004398 |
| method.UIRenderSystem._render_ui | 9880 | 1.111034 | 0.004130 |
| profile.unit_visible_cull | 9880 | 0.723763 | 0.003604 |
| profile.MapRenderSystem | 9880 | 2.656726 | 0.003376 |
| profile.UnitRenderSystem | 9880 | 3.965304 | 0.003337 |
| profile.PanelRenderSystem | 9880 | 0.155263 | 0.002916 |
| profile.MiniMapSystem | 9880 | 0.057349 | 0.002573 |
| sdl.draw.circle | 36841 | 0.002524 | 0.002524 |
| profile.render_queue_clear | 9880 | 0.003163 | 0.002501 |
| method.EffectRenderSystem._render_projectiles | 9880 | 0.002471 | 0.002471 |
| profile.EffectRenderSystem | 9880 | 0.314552 | 0.002385 |
| method.MiniMapSystem.update | 9880 | 0.054775 | 0.002359 |
| profile.effect_attack_indicators | 9880 | 0.205395 | 0.002308 |
| profile.map_overscan_tile_raster | 30 | 0.004514 | 0.002256 |
| profile.effect_selection | 9880 | 0.002776 | 0.002217 |
| profile.fog_surface_patch | 956 | 0.002612 | 0.002131 |
| profile.render_queue_prepare | 9880 | 0.002125 | 0.002125 |
| profile.effect_projectiles | 9880 | 0.004545 | 0.002074 |
| profile.UIRenderSystem | 9880 | 1.114801 | 0.002071 |
| profile.effect_attack_effects | 9880 | 0.085188 | 0.002069 |
| profile.effect_hover | 9880 | 0.002328 | 0.001970 |
| profile.AnimationSystem | 9880 | 0.003093 | 0.001923 |
| method.EffectRenderSystem._render_explosion_effect | 770 | 0.002013 | 0.001778 |
| method.UIRenderSystem.update | 9880 | 1.112730 | 0.001696 |
| method.EffectRenderSystem._render_single_effect | 8477 | 0.011531 | 0.001571 |
| profile.effect_position_index | 9880 | 0.001454 | 0.001454 |
| method.MapRenderSystem._get_visible_tiles_smart | 9880 | 0.001448 | 0.001448 |
| sdl.draw.line | 22027 | 0.001263 | 0.001263 |
| method.AnimationSystem.update | 9880 | 0.001171 | 0.001171 |
| method.PanelRenderSystem._render_selected_unit_info | 9880 | 0.000741 | 0.000741 |
| rms.clear | 9880 | 0.000662 | 0.000662 |
| method.UIRenderSystem._render_stats_panel | 9880 | 0.000620 | 0.000620 |
| method.MapRenderSystem._render_direct_outside_cached_overlap | 36 | 0.166698 | 0.000595 |
| method.MapRenderSystem._render_coordinates_optimized | 9880 | 0.000563 | 0.000563 |
| method.EffectRenderSystem._render_selection_effects | 9880 | 0.000559 | 0.000559 |
| sdl.draw.polygon | 5642 | 0.000482 | 0.000482 |
| profile.map_overscan_candidate_scan | 8 | 0.000476 | 0.000476 |
| method.UIRenderSystem._render_help_panel | 9880 | 0.000475 | 0.000475 |
| method.EffectRenderSystem._render_melee_aim_line | 978 | 0.000500 | 0.000449 |
| method.EffectRenderSystem._render_tile_hover | 9880 | 0.000358 | 0.000358 |
| profile.map_terrain_opaque_present_cache_build | 1 | 0.000213 | 0.000213 |
| profile.map_overscan_surface_allocate | 1 | 0.000049 | 0.000049 |
| profile.map_overscan_build_step | 37 | 0.005236 | 0.000032 |
| method.MapRenderSystem._build_job_matches_view | 36 | 0.000010 | 0.000010 |
| sdl.transform.scale | 3 | 0.000008 | 0.000008 |
| method.MapRenderSystem._build_terrain_present_cache | 1 | 0.000214 | 0.000001 |

## reuse_typed

9880个完整tick，同一扩展。

| scope | calls | inclusive ms/tick | self ms/tick |
|---|---:|---:|---:|
| method.MapRenderSystem._render_territory_boundaries_optimized | 9880 | 2.708705 | 2.708705 |
| profile.render_scalar_execute | 2439536 | 1.151404 | 1.076676 |
| method.UnitRenderSystem._get_visible_units | 9880 | 0.841030 | 0.841030 |
| rms.draw | 3916182 | 0.905015 | 0.753090 |
| method.UnitRenderSystem._render_single_unit_fast | 3337364 | 1.973634 | 0.725663 |
| method.UnitRenderSystem._render_units_batch | 9880 | 3.572261 | 0.669949 |
| method.UIRenderSystem._current_faction_counts | 9880 | 0.557110 | 0.557110 |
| method.UnitRenderSystem._get_fast_animation_screen_position | 3337364 | 0.528881 | 0.528881 |
| profile.render_queue_submit | 9880 | 2.022249 | 0.485327 |
| method.UnitRenderSystem._render_simple_health_bar | 703430 | 0.480908 | 0.408172 |
| method.UnitRenderSystem._render_unit_group_optimized | 3107767 | 2.331132 | 0.399797 |
| profile.render_batch_blits | 491898 | 0.265353 | 0.265353 |
| method.UnitRenderSystem.update | 9880 | 4.598109 | 0.173393 |
| profile.render_batch_pack | 754097 | 0.120165 | 0.120165 |
| rms._add_command | 6073794 | 0.111756 | 0.111756 |
| method.PanelRenderSystem._render_battle_log | 9880 | 0.132778 | 0.105074 |
| method.MapRenderSystem._render_terrain_direct | 35 | 0.157596 | 0.081050 |
| method.EffectRenderSystem._render_attack_effects | 9880 | 0.093716 | 0.080575 |
| construct.BlitCommand | 3916182 | 0.079208 | 0.079208 |
| method.MapRenderSystem._render_fog_of_war_optimized | 9880 | 0.085154 | 0.077456 |
| sdl.draw.rect | 2139930 | 0.074399 | 0.074399 |
| method.EffectRenderSystem._render_attack_indicators | 9880 | 0.057070 | 0.056475 |
| method.MiniMapSystem._render_minimap | 9880 | 0.057170 | 0.045084 |
| construct.DrawCommand | 2157612 | 0.035657 | 0.035657 |
| method.UIRenderSystem._render_faction_status_indicators | 9880 | 0.597504 | 0.031702 |
| method.UIRenderSystem._render_real_time_info | 9880 | 0.625525 | 0.023015 |
| method.PanelRenderSystem._render_view_mode_info | 9880 | 0.029655 | 0.022515 |
| method.MapRenderSystem.update | 9880 | 3.001724 | 0.017115 |
| method.UIRenderSystem._render_game_info | 9880 | 0.641635 | 0.013234 |
| method.MapRenderSystem._get_terrain_texture | 333600 | 0.012803 | 0.012803 |
| method.EffectRenderSystem.update | 9880 | 0.178838 | 0.011301 |
| method.MapRenderSystem._render_map_optimized | 9880 | 0.188162 | 0.010903 |
| method.MapRenderSystem._draw_overscan | 9845 | 0.013970 | 0.007502 |
| method.MiniMapSystem._render_camera_viewport | 9880 | 0.008161 | 0.006891 |
| method.EffectRenderSystem._render_slash_effect | 7142 | 0.009099 | 0.005738 |
| method.PanelRenderSystem.update | 9880 | 0.168014 | 0.004845 |
| profile.unit_visible_cull | 9880 | 0.845558 | 0.004529 |
| method.UIRenderSystem._render_ui | 9880 | 0.647310 | 0.004325 |
| profile.MapRenderSystem | 9880 | 3.005842 | 0.004118 |
| profile.UnitRenderSystem | 9880 | 4.601485 | 0.003376 |
| profile.PanelRenderSystem | 9880 | 0.171363 | 0.003349 |
| sdl.draw.circle | 36841 | 0.002915 | 0.002915 |
| profile.render_queue_clear | 9880 | 0.003788 | 0.002882 |
| method.MiniMapSystem.update | 9880 | 0.059925 | 0.002755 |
| profile.fog_surface_patch | 956 | 0.003224 | 0.002694 |
| profile.effect_projectiles | 9880 | 0.004962 | 0.002580 |
| profile.render_queue_prepare | 9880 | 0.002552 | 0.002552 |
| profile.MiniMapSystem | 9880 | 0.062395 | 0.002470 |
| profile.UIRenderSystem | 9880 | 0.651563 | 0.002414 |
| profile.EffectRenderSystem | 9880 | 0.181229 | 0.002390 |
| method.EffectRenderSystem._render_projectiles | 9880 | 0.002382 | 0.002382 |
| profile.effect_selection | 9880 | 0.002979 | 0.002373 |
| profile.effect_attack_indicators | 9880 | 0.059388 | 0.002318 |
| profile.map_overscan_tile_raster | 29 | 0.004364 | 0.002226 |
| profile.effect_attack_effects | 9880 | 0.095940 | 0.002223 |
| profile.effect_hover | 9880 | 0.002513 | 0.002063 |
| profile.AnimationSystem | 9880 | 0.003414 | 0.002056 |
| method.EffectRenderSystem._render_explosion_effect | 770 | 0.002225 | 0.001975 |
| method.MapRenderSystem._get_visible_tiles_smart | 9880 | 0.001944 | 0.001944 |
| method.UIRenderSystem.update | 9880 | 0.649149 | 0.001839 |
| method.EffectRenderSystem._render_single_effect | 8477 | 0.013142 | 0.001818 |
| profile.effect_position_index | 9880 | 0.001755 | 0.001755 |
| sdl.draw.line | 22027 | 0.001497 | 0.001497 |
| method.AnimationSystem.update | 9880 | 0.001358 | 0.001358 |
| rms.clear | 9880 | 0.000907 | 0.000907 |
| method.PanelRenderSystem._render_selected_unit_info | 9880 | 0.000736 | 0.000736 |
| method.UIRenderSystem._render_stats_panel | 9880 | 0.000677 | 0.000677 |
| method.UIRenderSystem._render_help_panel | 9880 | 0.000673 | 0.000673 |
| method.MapRenderSystem._render_coordinates_optimized | 9880 | 0.000645 | 0.000645 |
| method.EffectRenderSystem._render_selection_effects | 9880 | 0.000606 | 0.000606 |
| method.MapRenderSystem._render_direct_outside_cached_overlap | 35 | 0.158163 | 0.000567 |
| method.EffectRenderSystem._render_melee_aim_line | 978 | 0.000595 | 0.000539 |
| sdl.draw.polygon | 5642 | 0.000530 | 0.000530 |
| profile.map_overscan_candidate_scan | 8 | 0.000464 | 0.000464 |
| method.EffectRenderSystem._render_tile_hover | 9880 | 0.000450 | 0.000450 |
| profile.map_terrain_opaque_present_cache_build | 1 | 0.000208 | 0.000208 |
| profile.map_overscan_surface_allocate | 1 | 0.000059 | 0.000059 |
| profile.map_overscan_build_step | 36 | 0.005057 | 0.000021 |
| method.MapRenderSystem._build_job_matches_view | 35 | 0.000010 | 0.000010 |
| sdl.transform.scale | 3 | 0.000004 | 0.000004 |
| method.MapRenderSystem._build_terrain_present_cache | 1 | 0.000209 | 0.000001 |

## 绘制/缓存契约

| 输入/保留 | 既有机制 | E7依赖/失效 |
|---|---|---|
| Unit位置、动画、Health、样式、文字 | 原空间筛选、分组、字体/标签 | 不改，不跨帧缓存最终Unit绘制 |
| Map地形、viewport、zoom | opaque overscan和direct fallback | 不改；研究仅缓存校验过的坐标快照，≤32768 |
| MapData.tiles | 可原地更新字典 | ID每帧读取，非标准容器/ID回原方法 |
| TerritoryControl归属、progress、fortification | 原领地遍历/样式计算 | 任意live成员存在即原方法，不缓存字段 |
| Fog/阵营/epoch/journal | 既有FogPresenter patch/rebuild | 不改 |
| UI/选择/规则/纹理/字体 | 原展示读取及已有Surface缓存 | 不改，不新增计算结果缓存 |
| RMS/layer/painter order | 原Command、连续plain blits | 不改，不重排、少画或跨栅栏合批 |
| reset/close/场景/多实例 | World资源生命周期 | 坐标cache在cleanup删除；无实体/World/Surface引用新增 |

无领地组件并非全地图不需要领地显示；新增组件会立即回原方法。正收益范围只能由正式完整显示段验证。

真实Cocoa短诊断聚合含预热；1800个测量帧与聚合scope分母不能混用。两次诊断guard失败全部保留，不代表运行验收通过。
