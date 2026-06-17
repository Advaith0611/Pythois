# Pythios Autonomous Builder Agent

## Summary

Build a Groq-powered agent that turns a user prompt plus canvas screenshot/context into a fully built, researched, cited, deployed project at:

```text
https://pythios.xyz/apps/<6-char-code>
```

Each run should produce structured JSON, base64-encoded project files, citations, screenshots, deployment metadata, and a reusable tool manifest for future agents.

The system should use isolated ephemeral containers, remote artifact storage, and automatic cleanup so generated work does not accumulate on the local machine.

## Core Architecture

Keep the existing canvas entry shape:

```python
run(canvas_state, visual_context, prompt)
```

Add a builder pipeline behind it:

1. Intake: read prompt, canvas objects, uploaded files, webpage embeds, and screenshot.
2. Research: gather current web information when needed and store cited source records.
3. Spec: convert the request into a build plan, requirements, acceptance criteria, and tool choices.
4. Generate: create project files as structured file objects with base64 data URLs.
5. Build/Test: run install, lint, tests, browser validation, and screenshot capture in an isolated container.
6. Deploy: publish to `pythios.xyz/apps/<code>`.
7. Register Tool: save a small manifest so future agents can reuse the app.
8. Cleanup: delete local/container workspace after uploading required artifacts.

## Structured Output Contract

Return one machine-readable object, for example `pythios.project_build.v1`, containing:

- `projectCode`: six lowercase alphanumeric characters, collision-checked before deploy.
- `status`: `success`, `partial_success`, or `failed`.
- `deployment`: public URL, health status, and build logs summary.
- `files`: array of `{ path, mimeType, encoding: "base64", contentBase64, sizeBytes, role }`.
- `citations`: array of `{ id, title, url, publisher, accessedAt, usedFor }`.
- `screenshots`: base64 PNG screenshots from browser validation.
- `toolManifest`: reusable metadata for future agents.
- `actionBatch`: existing canvas actions that create a project card, screenshot, manifest file, and deployment link on the whiteboard.
- `errors`: structured recoverable and fatal errors.

Large files should be uploaded to object storage after generation. The structured output can include base64 for handoff, but permanent storage should keep only remote artifact references plus the reusable manifest.

## Implementation Changes

- Add a Groq client wrapper with structured-output prompting, retry logic, JSON schema validation, and model configuration through environment variables.
- Add orchestration modules for planner, researcher, code generator, build runner, deployment publisher, browser validator, and tool registry.
- Use isolated containers for all generated code execution with restricted secrets, network policy, CPU/memory/time limits, and disposable workspace directories.
- Deploy full-stack projects behind `pythios.xyz/apps/<code>`.
- Serve static apps directly from uploaded build artifacts.
- Route full-stack apps to a generated service/container plus static frontend assets.
- Keep the public route stable as `https://pythios.xyz/apps/<code>`.
- Store project metadata, deployment URL, citations, tool manifest, and status in Postgres.
- Store base64-decoded file blobs, screenshots, logs, and build artifacts in object storage.
- Keep local/container filesystem temporary only and delete it after upload.

## Tool Reuse Design

Each deployed app becomes a discoverable tool through a manifest registry.

Manifest fields should include:

- `toolId`
- `projectCode`
- `name`
- `description`
- `capabilities`
- `publicUrl`
- `inputSchema`
- `outputSchema`
- `examples`
- `artifactRefs`
- `citationRefs`
- `createdAt`
- `lastValidatedAt`

Future agents can retrieve tools by capability search, inspect their schemas, and either link users to them or call their APIs if the generated app exposes one.

## Test Plan

- Unit test project-code generation, collision handling, base64 file encoding, schema validation, citation formatting, and manifest creation.
- Integration test full build runs in an isolated container with cleanup verification.
- Browser test deployed apps at desktop and mobile sizes, capture screenshots, and verify the public route loads.
- Failure test bad generated code, failed deployment, missing citations, invalid JSON, oversized files, and network timeouts.
- Security test that generated code cannot access host files, backend secrets, or persistent local storage.

## Assumptions

- The builder should be fully automatic after the user asks it to build.
- Groq is the required LLM provider, with the exact model configurable.
- Generated apps should support full-stack projects, not only static sites.
- The canonical deployment URL is `https://pythios.xyz/apps/<6-char-code>`.
- Local storage should be ephemeral only; durable data belongs in remote DB/object storage.
- The current canvas action protocol remains the frontend integration layer.









codex resume 019eb6e6-50df-78f2-bcac-fed588b6313c
codex resume 019eba48-f787-7783-b609-5bcbca5e97e0