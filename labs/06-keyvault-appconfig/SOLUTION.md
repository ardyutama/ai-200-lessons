# Solution 06 — Key Vault + App Configuration (answer key)

> **Attempt-first rule.** First pass: you may consult this key. The two runs that count toward *Solid Practice* must be done with this file **closed**. When you're ready for a counted run, close it and work from [README.md](README.md) alone.

**The Case Thread.** SupportBrain calls an embedding API with a vendor key. That key belongs in Key Vault, never in config. Runtime switches, such as a beta re-ranker, belong in App Configuration. A sentinel key tells workers when to reload. Every block below is the next thing you do on that job.

**Setup (do once):**

```bash
floci az start && eval $(floci az env --format sdk-vars)   # README: AZURE_KEY_VAULT_ENDPOINT, AZURE_APP_CONFIGURATION_ENDPOINT
source ../../.venv/bin/activate                              # from this folder
```

The code uses `DefaultAzureCredential()`, the production pattern. Against floci-az, authenticate with the emulator's fixed dev credentials as ADR-0001 and the README describe. The calls below stay the same.

> **Note on the runtime split.** floci-az covers Key Vault and App Configuration (SETUP.md). Anything marked **Azure-side** is say-it-out-loud knowledge: Managed Identity, RBAC role assignment, and the Azure portal.

> **Verification status (2026-11-04).** Methods, properties, and content types were checked against the installed `azure-keyvault-secrets` and `azure-appconfiguration` packages. These blocks have **not** been run against floci-az yet.

---

## Block 1 — Secret versions

**Q.** Store the embedding key, rotate it, read the latest value with no version, read the old value by version, and list every version. What makes rotation invisible to readers that ask for the name only?

```python
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

vault = SecretClient(vault_url=os.environ["AZURE_KEY_VAULT_ENDPOINT"], credential=DefaultAzureCredential())

v1 = vault.set_secret("embedding-api-key", "key-2026-10")
vault.set_secret("embedding-api-key", "key-2026-11")                  # rotation = a new version, not an edit

print("latest :", vault.get_secret("embedding-api-key").value)        # no version -> newest
print("pinned :", vault.get_secret("embedding-api-key", version=v1.properties.version).value)
print("versions:", [p.version for p in vault.list_properties_of_secret_versions("embedding-api-key")])
```

**Why / trap.** A reader that omits the version always gets the newest enabled version, so it picks up rotation without a redeploy. A reader that pins a version keeps the old value forever. Rotation creates a version; it does not edit one. The secret's **name** is the stable handle.

---

## Block 2 — Rotation narrative: one DB password, twelve apps

**Q.** The database password is used by 12 apps. Describe the rotation in order, and say how each app picks up the change.

**A.** (1) Set a new version of the secret in Key Vault. (2) Change the database to accept the new password. (3) The apps read the latest version, so they pick it up with no redeploy. Apps that cache the value must reload it.

**Why / trap.** App Service Key Vault references re-fetch every 24 hours, and any configuration change restarts the app and re-fetches at once (Learn, Key Vault references article). Keys are a different object type, with their own rotation policies, and the README covers them separately. Exam line: *rotate by version, not by vault or by app redeploy.*

---

## Block 3 — Protection features and access

**Q.** Two settings protect against accidental or malicious deletion. Which one only allows recovery, and which one blocks purging? Then: which access model is recommended, and which built-in role can read secret values?

**A.** Soft-delete allows recovery. Purge protection blocks purging. Azure RBAC is the recommended model. Key Vault Secrets User reads secret contents, and Key Vault Reader reads metadata only.

**Why / trap.**

| Setting | Default | What it means |
|---|---|---|
| Soft-delete | On for new vaults; retention 90 days by default (7 to 90 allowed) | A deleted vault or object is recoverable. It cannot be turned off once enabled. |
| Purge protection | Off | A deleted vault or object cannot be purged until its retention period ends. |
| Azure RBAC vs access policy | RBAC is recommended; from API version 2026-02-01, RBAC is the default for new vaults | Access policies are the legacy data-plane model. |

Pick the role by the job: a monitoring tool that lists expiry dates needs **Key Vault Reader**. An app that reads values needs **Key Vault Secrets User**. Admins who create secrets need **Key Vault Secrets Officer**.

---

## Block 4 — App Configuration labels: one key, two environments

**Q.** Store `app:theme` as `blue` for label `dev` and `green` for label `prod`, then read both.

```python
import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from azure.identity import DefaultAzureCredential

appcfg = AzureAppConfigurationClient(
    base_url=os.environ["AZURE_APP_CONFIGURATION_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

appcfg.set_configuration_setting(ConfigurationSetting(key="app:theme", label="dev", value="blue"))
appcfg.set_configuration_setting(ConfigurationSetting(key="app:theme", label="prod", value="green"))

print(appcfg.get_configuration_setting(key="app:theme", label="dev").value)    # blue
print(appcfg.get_configuration_setting(key="app:theme", label="prod").value)   # green
```

**Why / trap.** A label is an environment dimension on the same key. The reader chooses the label, so one store serves several environments. Labels separate environments; they are not a security boundary, so secrets still go in Key Vault.

---

## Block 5 — Feature flag

**Q.** Create the feature flag `beta-ui` and print the key and content type App Configuration stores for it.

```python
from azure.appconfiguration import FeatureFlagConfigurationSetting

flag = FeatureFlagConfigurationSetting("beta-ui", enabled=True)
appcfg.set_configuration_setting(flag)
print(flag.key, flag.content_type)
# .appconfig.featureflag/beta-ui  application/vnd.microsoft.appconfig.ff+json;charset=utf-8
```

**Why / trap.** The SDK stores a feature flag as a special key under `.appconfig.featureflag/` with its own content type. Filters decide when the flag is on. The portal's built-in filter types are **Time window** (a date range) and **Targeting** (named users and groups). The Learn example for a 50 percent rollout uses a **custom** filter with a `Percentage` parameter, so name it as custom in an answer.

---

## Block 6 — Key Vault reference: the pointer lives in config, the value in the vault

**Q.** Put the embedding key behind an App Configuration key without copying its value into config.

```python
from azure.appconfiguration import SecretReferenceConfigurationSetting

vault_url = os.environ["AZURE_KEY_VAULT_ENDPOINT"].rstrip("/")
ref = SecretReferenceConfigurationSetting("app:embedding-key", f"{vault_url}/secrets/embedding-api-key")
appcfg.set_configuration_setting(ref)
print(ref.content_type)   # application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8
print(ref.value)          # {"uri": "https://.../secrets/embedding-api-key"}
```

**Why / trap.** The store holds only the URI. A reader needs read access to App Configuration **and** the Key Vault Secrets User role on the secret. Without the second grant, resolution fails, and the value is not returned to the app. Secrets never sit in the config store.

---

## Block 7 — Sentinel refresh: watch one key, not forty

**Q.** A deploy changes 40 keys. The workers should reload once. Write a check that detects one change signal.

```python
def sentinel_moved(client: AzureAppConfigurationClient, last_etag: str | None) -> tuple[bool, str]:
    sentinel = client.get_configuration_setting(key="app:sentinel")
    return sentinel.etag != last_etag, sentinel.etag
```

**Why / trap.** Update `app:sentinel` once, after the batch. Workers that watch only the sentinel reload once per deploy. Watching 40 keys means 40 triggers and a risk of partial reads mid-deploy. The provider library (`azure-appconfiguration-provider`) offers a `refresh_on` option for the same pattern. It is not in `requirements.txt`, so this lab does the check by hand.

---

## Done-when check

- [ ] Blocks 1, 4, and 6 written twice from memory
- [ ] You can draw the triangle: App Configuration holds the pointer, Key Vault holds the value, and a managed identity holds read access to both
- [ ] You can write the Key Vault secret URI cold: `https://<vault-name>.vault.azure.net/secrets/<secret-name>[/<version>]`

Cleanup: `floci az stop`.
