# Secrets & Roles — Verified Cross-Service RBAC Cheat Sheet (retake1)

**How to read "plane":**
- `control` — permissions live under the role's **Actions** (and/or `*/read`), authorized via Azure Resource Manager; manages the resource itself, not the data inside it.
- `data` — permissions live under **DataActions**, authorized against the service's own data endpoint.
- `data (native)` — Cosmos DB only: a data-plane permission system that is **not Azure RBAC at all**; it's a parallel, account-scoped role system with its own CLI (`az cosmosdb sql role ...`).
- `data-like (Actions)` — ACR's legacy roles: they govern data (image pull/push) but are technically defined via `Actions`, not `DataActions` (a historical exception to the usual rule).
- `control-ish (Actions)` — Monitor/Log Analytics read/query roles: classified as `Actions` even though querying telemetry feels like "data" (another historical exception).
- `control*` — Key Vault roles that Microsoft's own docs list in its "data plane operations" table, but whose actual role-definition JSON has **zero DataActions** (verified against the live ARM role definitions, Nov 2026): the permission is 100% under `Actions`/`*/read`. Grouped with the data-plane roles for workflow purposes (they gate access to vault *data*), not because the permission itself is a DataAction.

Every role name below was read directly from an official Microsoft Learn/Azure docs page during this research session (see URL column); none are guessed.

## Key Vault — `azure/key-vault/general/rbac-guide`

| Service | Role | Plane | Allows | URL |
|---|---|---|---|---|
| Key Vault | Key Vault Administrator | data | All data-plane ops (keys, secrets, certs); cannot manage the vault resource or role assignments | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Reader | data | Read object **metadata** (names/properties) only — never secret values or key material | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Purge Operator | control* | Permanently purge soft-deleted vaults — the role's only action is `Microsoft.KeyVault/locations/deletedVaults/purge/action` (ARM/management-plane, 0 DataActions); Microsoft's own doc groups it with the data-plane role list anyway | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Certificates Officer | data | Any action on certificates except managing permissions | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Certificate User | data | Read entire certificate, including the private key | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Crypto Officer | data | Any action on keys except managing permissions | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Crypto Service Encryption User | data | Read key metadata + wrap/unwrap only (used by services like Storage encryption) | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Crypto User | data | Perform cryptographic operations (encrypt/decrypt/sign/verify) with existing keys | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Crypto Service Release User | data | Release keys for Azure Confidential Computing / equivalent environments | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Secrets Officer | data | Any action on secrets except managing permissions | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Secrets User | data | Read secret contents, including the secret portion of a certificate with a private key | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Data Access Administrator | control* (meta) | Manage role assignments for the other KV data-plane roles — but via `Microsoft.Authorization/roleAssignments/{write,delete}` (ARM/control-plane, 0 DataActions), not a Key Vault DataAction; ABAC-aware; grants no read/write itself | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |
| Key Vault | Key Vault Contributor | control | Manage the vault resource (create/delete/update properties); **no** key/secret/cert access | https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide |

**Defaults verified on the same page:** Azure RBAC is the **default** permission model for new vaults as of API version `2026-02-01`+ (legacy access policies still exist, must be chosen explicitly now). Soft delete: on by default, 7–90 days retention (default 90), can't be disabled once on. Purge protection: **off** by default, optional, irreversible once on. Throttling (`azure/key-vault/general/overview-throttling`): 4,000 GETs / 300 writes per vault per 10s; subscription aggregate = 5× one vault's limit; 429 → exponential backoff.

## App Configuration — `azure/azure-app-configuration/concept-enable-rbac`

| Service | Role | Plane | Allows | URL |
|---|---|---|---|---|
| App Configuration | App Configuration Data Owner | data | Read, write, delete App Configuration data (key-values, feature flags, snapshots) | https://learn.microsoft.com/en-us/azure/azure-app-configuration/concept-enable-rbac |
| App Configuration | App Configuration Data Reader | data | Read-only on App Configuration data | https://learn.microsoft.com/en-us/azure/azure-app-configuration/concept-enable-rbac |
| App Configuration | App Configuration Contributor | control | Manage the resource; can **enable access-key auth** and then read/write data that way (indirect data backdoor unless blocked by Azure Policy) | https://learn.microsoft.com/en-us/azure/azure-app-configuration/concept-enable-rbac |
| App Configuration | App Configuration Reader | control | Read the resource only; no data, no access keys | https://learn.microsoft.com/en-us/azure/azure-app-configuration/concept-enable-rbac |

Role-assignment propagation: allow up to **15 minutes** (App Configuration) — contrast with ~5 min (Service Bus/Event Hubs) and ~10 min (Functions general guidance, per `functions-identity-based-connections-tutorial`).

## Messaging: Service Bus & Event Hubs

| Service | Role | Plane | Allows | URL |
|---|---|---|---|---|
| Service Bus | Azure Service Bus Data Owner | data | Full access: send, receive, and manage all entities (queues/topics/subscriptions/filters) | https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-managed-service-identity |
| Service Bus | Azure Service Bus Data Sender | data | Send messages only | https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-managed-service-identity |
| Service Bus | Azure Service Bus Data Receiver | data | Receive messages only | https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-managed-service-identity |
| Event Hubs | Azure Event Hubs Data Owner | data | Full access to Event Hubs resources | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/analytics |
| Event Hubs | Azure Event Hubs Data Sender | data | Send events only | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/analytics |
| Event Hubs | Azure Event Hubs Data Receiver | data | Receive events only | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/analytics |

**Trap:** to trigger from a Service Bus **topic subscription**, the role assignment needs effective scope over the **subscription** resource, not just the topic — the Azure portal doesn't expose that scope, so use the CLI (`functions-identity-based-connections-tutorial`).

## Event Grid — `azure/event-grid/security-authorization`

| Service | Role | Plane | Allows | URL |
|---|---|---|---|---|
| Event Grid | EventGrid Data Sender | data | Publish/send events to topics | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/integration |
| Event Grid | EventGrid Contributor | control | Create and manage Event Grid resources (topics, domains) | https://learn.microsoft.com/en-us/azure/event-grid/security-authorization |
| Event Grid | EventGrid EventSubscription Contributor | control | Manage event subscriptions (the routing config), not topics or event data | https://learn.microsoft.com/en-us/azure/event-grid/security-authorization |
| Event Grid | EventGrid EventSubscription Reader | control | Read event subscriptions | https://learn.microsoft.com/en-us/azure/event-grid/security-authorization |
| Event Grid | EventGrid TopicSpaces Publisher | data | Publish to MQTT topic spaces (Event Grid namespaces feature) | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/integration |
| Event Grid | EventGrid TopicSpaces Subscriber | data | Subscribe to MQTT topic spaces | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/integration |

## Storage — `azure/role-based-access-control/built-in-roles/storage`

| Service | Role | Plane | Allows | URL |
|---|---|---|---|---|
| Storage | Storage Blob Data Owner | data | Full permissions on containers + blobs, including POSIX ACL assignment | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |
| Storage | Storage Blob Data Contributor | data | Read, write, delete containers + blobs | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |
| Storage | Storage Blob Data Reader | data | Read/list containers + blobs | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |
| Storage | Storage Queue Data Contributor | data | Read, write, delete queues + queue messages | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |
| Storage | Storage Queue Data Reader | data | Read/list queues + peek messages | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |
| Storage | Storage Queue Data Message Processor | data | Peek, retrieve, delete a message (consumer-only) | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |
| Storage | Storage Queue Data Message Sender | data | Add a message to a queue (producer-only) | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |
| Storage | Storage Table Data Contributor | data | Read, write, delete table entities | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |
| Storage | Storage Table Data Reader | data | Read table entities | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |
| Storage | Storage Account Contributor | control | Manage the storage account resource; **also grants access to the account key** (Shared Key data access) | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |
| Storage | Reader and Data Access | control | View account, can't create/delete it, but **can list account keys** → full read/write to all data via Shared Key | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/storage |

**Functions least-privilege table (verified from `functions-identity-based-connections-tutorial`):** `AzureWebJobsStorage` (host) → **Storage Blob Data Owner** (+ **Storage Table Data Contributor** for host diagnostics); Blob trigger → Blob Data Owner + Queue Data Contributor (poison queue); Blob output → Blob Data Owner; Queue trigger → Queue Data Reader + Message Processor; Queue output → Queue Data Contributor + Message Sender; Table input/output → Table Data Reader / Table Data Contributor; Event Hub trigger → host storage needs Blob Data Owner (checkpoints); Timer trigger → host storage needs Blob Data Owner (singleton lock); Durable Functions → Blob Data Contributor + Queue Data Contributor + Table Data Contributor.

## Cosmos DB — control plane is Azure RBAC, data plane is native

| Service | Role | Plane | Allows | URL |
|---|---|---|---|---|
| Cosmos DB | Cosmos DB Operator | control | Manage/scale the account; **cannot** grant data access or read keys | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/databases |
| Cosmos DB | Cosmos DB Account Reader Role | control | Read account metadata | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/databases |
| Cosmos DB | DocumentDB Account Contributor | control | Full control-plane management of the account | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/databases |
| Cosmos DB | CosmosBackupOperator / CosmosRestoreOperator | control | Backup / restore operations | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/databases |
| Cosmos DB | Cosmos DB Built-in Data Reader | **data (native)** | Read items, run queries, read the change feed — assign via `az cosmosdb sql role assignment create`, **not** `az role assignment create`; portal unsupported | https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/security/how-to-grant-data-plane-role-based-access |
| Cosmos DB | Cosmos DB Built-in Data Contributor | **data (native)** | Full CRUD, query, change feed, stored procedures, conflict feed — same native assignment mechanism | https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/security/how-to-grant-data-plane-role-based-access |

## Azure Container Registry — two generations

| Service | Role | Plane | Allows | URL |
|---|---|---|---|---|
| ACR | AcrPull | data-like (Actions) | Pull images, registry-wide | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| ACR | AcrPush | data-like (Actions) | Pull + push images, registry-wide | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| ACR | AcrDelete | data-like (Actions) | Delete repositories/tags/manifests | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| ACR | Container Registry Repository Reader | data | Read (pull) a **single repository** | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| ACR | Container Registry Repository Writer | data | Read + write (push) a single repository | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| ACR | Container Registry Repository Contributor | data | Read + write + delete a single repository | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| ACR | Container Registry Data Importer and Data Reader | control action + data | Import images into the registry (`importImage`) + pull/list repositories | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |

## Azure Kubernetes Service — credential-fetch vs true RBAC authorization

| Service | Role | Plane | Allows | URL |
|---|---|---|---|---|
| AKS | Azure Kubernetes Service Cluster Admin Role | control | List the **cluster-admin** kubeconfig credential (bypasses Kubernetes/Entra RBAC once used) | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| AKS | Azure Kubernetes Service Cluster User Role | control | List the **cluster-user** kubeconfig credential (still subject to k8s/Entra RBAC) | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| AKS | Azure Kubernetes Service RBAC Reader | data | Read most namespace objects; **excludes Secrets** (anti-privilege-escalation) | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| AKS | Azure Kubernetes Service RBAC Writer | data | Read/write most namespace objects; **includes Secrets** → can impersonate any ServiceAccount in the namespace | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| AKS | Azure Kubernetes Service RBAC Admin | data | Manage all namespace resources except resourcequotas/namespaces themselves | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| AKS | Azure Kubernetes Service RBAC Cluster Admin | data | Manage all resources in the cluster, no exclusions | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |

## Azure Managed Redis — Entra identity list, not Azure RBAC

| Service | Role | Plane | Allows | URL |
|---|---|---|---|---|
| Azure Managed Redis | Azure Managed Redis Contributor | control | Manage the cache resource | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/databases |
| Azure Managed Redis | Azure Managed Redis Reader | control | Read the cache resource | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/databases |
| Azure Managed Redis | *(no Azure RBAC data-plane role)* | data | Entra principals are added directly as **cache users**; **full access to all commands/keys by default**; granular control only via a **preview** custom data-access-permissions feature, not Azure RBAC | https://learn.microsoft.com/en-us/azure/redis/entra-for-authentication |
| Azure Cache for Redis (classic) | Redis Cache Contributor | control | Manage the classic (non-Enterprise) cache resource | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/databases |

## Monitor / Log Analytics — `azure/role-based-access-control/built-in-roles/monitor`

| Service | Role | Plane | Allows | URL |
|---|---|---|---|---|
| Monitor | Monitoring Metrics Publisher | data | Write custom metrics/telemetry only (`Microsoft.Insights/Metrics/Write`) | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/monitor |
| Monitor | Monitoring Reader | control-ish (Actions) | Read all metrics/logs across resources; can run Log Analytics search queries | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/monitor |
| Monitor | Monitoring Contributor | control | Broadly edit monitoring config (alerts, workbooks, diagnostic settings) | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/monitor |
| Log Analytics | Log Analytics Reader | control-ish (Actions) | Query/search workspace data; explicitly **excludes** workspace shared keys | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/monitor |
| Log Analytics | Log Analytics Contributor | control-ish (Actions) + 1 DataAction | Edit monitoring settings, install VM extensions, read storage keys for log collection, export workspace data | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/monitor |

## App Service / Functions & Container Apps — `built-in-roles/web-and-mobile`, `built-in-roles/containers`

| Service | Role | Plane | Allows | URL |
|---|---|---|---|---|
| App Service / Functions | Website Contributor | control | Manage web apps / function apps (not App Service Plans); **no Azure RBAC data-plane role exists** for app content — deployment uses publish credentials / OIDC instead | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/web-and-mobile |
| Container Apps | Container Apps Contributor | control | Full management of Container Apps | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| Container Apps | Container Apps Operator | control + 1 DataAction | Read a Container App + logstream/exec/debug into it; no modify | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| Container Apps | Container Apps ManagedEnvironments Contributor | control | Manage the Container Apps environment resource | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |
| Container Apps | Container Apps ManagedEnvironments Reader | control | Read the environment resource | https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles/containers |

## Cross-service unifying trap: "control-plane role with a data backdoor via keys"

Four services repeat the same pattern — a role that sounds control-plane-only but indirectly grants data access because it can read/regenerate a key or set an access policy:

| Service | Role | Backdoor mechanism |
|---|---|---|
| Key Vault | Key Vault Contributor | Can set its own access policy on an access-policy-model vault, self-granting data access |
| App Configuration | App Configuration Contributor | Can enable access-key authentication, then read/write data with that key |
| Storage | Storage Account Contributor / Reader and Data Access | Can list the account's Shared Keys, then read/write all data with them |
