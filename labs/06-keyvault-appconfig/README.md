# Lab 06 — Key Vault + App Configuration (floci-az)

**Study-guide bullets covered:** secure secrets with Key Vault including rotation and retrieval · store/retrieve app configuration.

**Setup:** `floci az start && eval $(floci az env --format sdk-vars)` → you get `AZURE_KEY_VAULT_ENDPOINT` and `AZURE_APP_CONFIGURATION_ENDPOINT`. Remember ADR-0001: locally you authenticate with the emulator's fixed credentials; in real Azure the pattern is `DefaultAzureCredential` + Managed Identity + Key Vault RBAC — know both.

## Steps

1. **Secrets lifecycle.** With `SecretClient`: `set_secret("db-password", ...)`, `get_secret(...).value`, then `set_secret` again — observe **versioning** (`properties.version`). List versions. Explain why consumers reading by name pick up rotation without redeploy.
2. **Rotation narrative.** Be able to answer: "rotate a DB password used by 12 apps" — new secret version + update the DB; apps read latest. Keys additionally have rotation policies.
3. **Protection features.** Soft-delete (default on, recoverable) vs purge protection (can't be permanently deleted before retention). RBAC vs legacy access policies — which is recommended.
4. **App Configuration.** With `azure-appconfiguration`: set `app:theme=blue` (label `dev`) and the same key with label `prod`. Read both. Explain labels as environment separation.
5. **Feature flag.** Create a feature flag (`.appconfig.featureflag/beta-ui`) and evaluate it; name the filter types (percentage, targeting, time window).
6. **Key Vault reference.** Store a configuration value that is a Key Vault reference (content type `application/vnd.microsoft.appconfig.keyvaultref+json`). Explain how the app resolves it transparently — secrets never live in the config store.
7. **Sentinel refresh.** Describe the sentinel-key pattern: bump `app:sentinel` to trigger a full config refresh; why that's better than watching every key.

## Done when

- [ ] Steps 1, 4, 6 done twice from memory
- [ ] You can draw the "App Configuration + Key Vault references + Managed Identity" triangle
- [ ] You can state the Key Vault URI format cold

## Cleanup

`floci az stop`
