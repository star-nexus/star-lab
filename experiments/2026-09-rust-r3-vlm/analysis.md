# Analysis — VLM native projection and display boundary

## 1. Observation

At exact API10, all 54 explicitly enabled VLM fixture calls fail as unimplemented after successful registration. Python returns faction JSON plus an image or frame_error. API11 matches all 54 full responses and exported authoritative states. Actual Cocoa captures match original Python byte-for-byte in four mode/view cases.

## 2. Competing hypotheses

H1: missing native dispatch/host image attachment. H2: visual decoding differences indicate a Rust renderer regression. H3: the current frame is independently projected for each querying faction.

## 3. Instrumentation / diagnostic changes

Full before/after requests, images, response and state traces; complete unit selection and trusted identity paths; capture errors; structured mixed-batch comparisons and pending writer tests. Actual Cocoa engine queries request Wei while UI view varies Wei/Shu. Reference capture uses original Python entry point on the same screen. Independent 3-pixel capture on old/new checkouts includes a direct TGA RLE packet read.

## 4. Evidence

H1 supported by old unimplemented errors and matching new dispatch/capture. H2 rejected for the observed pixel mismatch: Python/Rust bytes already equal; a no-world, no-native-runtime codec control reproduces the same RGB transformation in both versions. Stored TGA pixel bytes contain the transformed RGB. H3 rejected: capture does not switch UI view or redraw; the picture stays the existing screen, while JSON remains authorized to Wei.

## 5. Root cause

The native action dispatch lacked VLM; media needs Python's display stack. Image attachment after an entire batch would cross later action boundaries, so the adapter snapshots/validates the entire input then splits execution at VLM requests and holds one admission lock until attachment completes. Decoding errors, permission rejection and image errors retain original semantics. No native hot loop calls Python.

## 6. Causal chain

Trusted ingress → native permission/unit projection → existing framebuffer copy/encoding → attach result → admit later commands.
Legacy capture TGA output → transformed alpha-bearing RGB bytes → raw-screen RGB guard fails in both backends, despite byte-compatible responses.

## 7. Rejected explanations

Default mode rejecting VLM is not proof of implementation. JSON authorization is not proof of image-view isolation. An encoder label is not proof of PNG bytes. Equal native/legacy encoded output is evidence of migration compatibility, not lossless framebuffer encoding or real-model image delivery.

## 8. Limits of the evidence

Serial settings1/2/4 only. Mac CPython3.13/pygame2.6.1; no Linux/3.14. Global screen access must run on the application owner thread; one runtime admission lock cannot coordinate arbitrary external display writes. No new capacity, network or LLM ranking result. Old score impact unknown. Dynamic cold-component coverage remains R002.

## 9. Raw evidence

Formal before/after, vlm-window, codec-before/after, players, window and replay directories. The initial failed pixel guard is an intermediate valid diagnostic, not a passing lossless-image gate. Codec after media cross-reference canonical before bytes; original old scene trace stays in its previous archive.
