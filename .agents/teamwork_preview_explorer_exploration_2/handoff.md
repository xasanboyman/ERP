# Frontend Codebase Investigation Report: Cutting Orders & Avatar Rows

## 1. Observation

### File Paths & Key Code Snippets

#### A. Cutting Orders View (`Front/src/views/Cutting/Cutting.vue`)
* **State definition** (lines 218-227):
  ```typescript
  const form = reactive({
    id: '',
    order_number: '',
    project: '',
    order_name: '',
    document_date: '',
    responsible_user_ids: [] as string[],
    status: 'created',
    items: [] as any[]
  })
  ```
* **API Invocations**:
  * Fetching list: `getOrderListApi()` called on line 168.
  * Saving order: `saveOrderApi(form)` called on line 300.
  * Deleting order: `deleteOrderApi({ ids: [row.id] })` called on line 321.
  * Start production: `startProductionApi({ orderId: row.id })` called on line 335.
* **Gaps Identified**:
  * The order listing `<el-table>` (lines 23-60) does not contain a column to display the responsible users.
  * The add/edit order form `<el-dialog>` (lines 63-121) has no input field/selector for `responsible_user_ids`.
  * The `openAddDialog` method (lines 233-243) does not reset `form.responsible_user_ids` to `[]`.
  * The `openEditDialog` method (lines 245-255) does not initialize `form.responsible_user_ids` from `row.responsible_user_ids`.

#### B. Avatars Component (`Front/src/components/Avatars/src/Avatars.vue`)
* **Properties** (lines 11-28):
  ```typescript
  const props = defineProps({
    size: {
      type: [String, Number] as PropType<ComponentSize | number>,
      default: ''
    },
    max: {
      type: Number,
      default: 5
    },
    data: {
      type: Array as PropType<AvatarItem[]>,
      default: () => []
    },
    showTooltip: {
      type: Boolean,
      default: true
    }
  })
  ```
* **Render Logic & Stacking** (lines 33-69):
  ```html
  <template>
    <div :class="prefixCls" class="flex items-center">
      <template v-for="item in filterData" :key="item.url">
        <template v-if="showTooltip && item.name">
          <ElTooltip :content="item.name" placement="top">
            <ElAvatar
              :size="size"
              :src="item.url"
              class="relative"
              :style="{
                zIndex: filterData.indexOf(item)
              }"
            />
          </ElTooltip>
        </template>
        ...
      </template>

      <ElAvatar
        v-if="data.length > max"
        :style="{
          zIndex: data.length
        }"
      >
        <span>+{{ data.length - max }}</span>
      </ElAvatar>
    </div>
  </template>
  ```
* **Style Overrides for Overlapping** (lines 74-78):
  ```less
  .@{prefix-cls} {
    .@{elNamespace}-avatar + .@{elNamespace}-avatar {
      margin-left: -15px;
    }
  }
  ```
* **AvatarItem Type definition** (`Front/src/components/Avatars/src/types/index.ts` lines 1-4):
  ```typescript
  export interface AvatarItem {
    url: string
    name?: string
  }
  ```

#### C. API Clients
* **Cutting APIs** (`Front/src/api/cutting/index.ts` lines 27-41):
  * `getOrderListApi` maps to `GET /cutting/order/list`.
  * `saveOrderApi` maps to `POST /cutting/order/save`.
  * `startProductionApi` maps to `POST /cutting/order/start-production`.
* **User List API** (`Front/src/api/login/index.ts` lines 16-24):
  * `getUserListApi` maps to `GET /mock/user/list`.
* **Request Interceptor** (`Front/src/axios/service.ts` lines 19-22):
  ```typescript
  if (res.url && res.url.startsWith('/mock')) {
    res.url = res.url.replace(/^\/mock/, '')
  }
  ```
  This strips the `/mock` prefix, routing requests to the actual backend API endpoints (e.g., `/user/list`).

#### D. Backend Endpoints
* **User List Endpoint** (`Back/app/routers/auth.py` lines 52-67):
  * `@router.get("/user/list")` returns user accounts with their `username` fields from the DB.
* **Cutting Order Endpoints** (`Back/app/routers/cutting.py` and `Back/app/crud.py` lines 380, 393):
  * Serializes and saves `responsible_user_ids` as a list of strings (usernames).

---

## 2. Logic Chain

1. **API Mapping**: The request interceptor in `Front/src/axios/service.ts` replaces `/mock` prefixes. Thus, a call to `getUserListApi` (defined with url `/mock/user/list`) resolves to `/user/list`. The backend (`Back/app/routers/auth.py`) implements `@router.get("/user/list")` which returns a list of database users including their `username`. This represents our source of assignable responsible users.
2. **Cutting Form Requirements**: The state definition in `Cutting.vue` includes `responsible_user_ids` inside the `form` reactive object. However, there is no corresponding `<el-select>` element in the UI dialog. To bridge this, a multi-select `<el-select>` element must be added to the form dialog, populated by fetching users via `getUserListApi()`.
3. **Cutting Form Lifecycle Integration**: In order to properly save and edit orders:
   * `openAddDialog` must reset `form.responsible_user_ids = []` to prevent pollution.
   * `openEditDialog` must populate `form.responsible_user_ids = row.responsible_user_ids ? [...row.responsible_user_ids] : []` to reflect the persisted list in the editor form.
4. **Displaying Avatars**: The `Avatars` component expects an array of `AvatarItem` containing `{ url: string, name?: string }`. In the FastAPI backend, `responsible_user_ids` holds string usernames. Therefore, in `Cutting.vue`, we must map usernames to `AvatarItem` objects. A local placeholder image (imported from `@/assets/imgs/avatar.jpg`) can be used as the `url`, while the username is mapped to the `name` property.
5. **Avatar Stacking & Overlap Behavior**:
   * **Stacking Order**: In `Avatars.vue`, `zIndex` is bound to the element's index in `filterData` (`filterData.indexOf(item)`). This ensures a left-to-right stacking (first avatar has `zIndex` 0, second has 1, third has 2, meaning later avatars layer on top of preceding ones). The "+N" avatar has the highest z-index (`data.length`), ensuring it is always on top.
   * **Overlapping**: The LESS style override applies a negative margin `margin-left: -15px` to any `.el-avatar` that follows another `.el-avatar` inside the `.avatars` container, producing the overlapping stacked avatar group layout.

---

## 3. Caveats

* **Avatar Images**: Since the system does not have individual user avatar upload endpoints/storage (other than personal center upload), all responsible users will visually display the same default avatar image (`@/assets/imgs/avatar.jpg`). Identification is handled solely by the hovered tooltip showing the `username` (facilitated by the `<ElTooltip>` component).
* **System Users vs Workers**: System users (representing administrative/managerial accounts) are distinct from physical workers (usta). The responsible users are fetched via `getUserListApi` (`/user/list`), while workers assigned to tasks and executions are fetched via `getWorkerListApi` (`/worker/list`).

---

## 4. Conclusion

The frontend represents a solid structure for cutting orders and avatar groups, but lacks the necessary UI bindings to assign and view `responsible_user_ids` in `Cutting.vue`.
* The `responsible_user_ids` field is saved and retrieved as a string list of usernames.
* Users can be assigned in `Cutting.vue` using a multi-select dropdown connected to `getUserListApi()`.
* The `Avatars` component implements horizontal overlapping via `margin-left: -15px` CSS rules and sequential `zIndex` sorting.
* An avatar column should be added to the order list table in `Cutting.vue` using `Avatars` and mapping usernames to `avatar.jpg` with their username as the tooltip content.

---

## 5. Verification Method

To verify these findings and the integration:
1. **Inspect Files**:
   * Verify the imports and reactive state structure in `Front/src/views/Cutting/Cutting.vue` around lines 145-155 and 218-227.
   * Verify properties, template structure, and LESS styles in `Front/src/components/Avatars/src/Avatars.vue`.
   * Verify endpoint definitions in `Front/src/api/cutting/index.ts` and `Front/src/api/login/index.ts`.
2. **Endpoint Behavior**:
   * Run the backend locally and check that `GET /user/list` and `GET /cutting/order/list` return the expected JSON payloads with code `0`.
