import re

# 1. Pos.vue
pos_path = '/home/xasanboy/ERP/Front/src/views/Sales/Pos.vue'
with open(pos_path, 'r', encoding='utf-8') as f:
    pos_content = f.read()

# fix openReceipt -> openReceiptDetail
pos_content = pos_content.replace("@click.stop=\"openReceipt(scope.row)\"", "@click.stop=\"openReceiptDetail(scope.row)\"")
pos_content = pos_content.replace(">Chek<", ">{{ t('erp.receipt') }}<")
# fix scanQuantity ref
pos_content = pos_content.replace("const scanQuantity = ref(1)", "const scanQuantity = ref<any>(1)")
pos_content = pos_content.replace("qtyToAdd: number = scanQuantity.value,", "qtyToAdd: number = Number(scanQuantity.value) || 1,")
# fix paidVal in handleCompleteCheckout
old_checkout = """const handleCompleteCheckout = async () => {
  if (!cart.value.length) return
  submittingCheckout.value = true
  try {
    const paidVal =
      checkoutForm.payment_method === 'nasiya' ? checkoutForm.paid_amount || 0 : grandTotal.value"""

new_checkout = """const handleCompleteCheckout = async () => {
  if (!cart.value.length) return
  submittingCheckout.value = true
  const paidVal =
    checkoutForm.payment_method === 'nasiya' ? checkoutForm.paid_amount || 0 : grandTotal.value
  try {"""
pos_content = pos_content.replace(old_checkout, new_checkout)

with open(pos_path, 'w', encoding='utf-8') as f:
    f.write(pos_content)
print("Fixed Pos.vue")

# 2. Debtors.vue: fix @click="fetchDebtors" -> @click="() => fetchDebtors()"
deb_path = '/home/xasanboy/ERP/Front/src/views/Sales/Debtors.vue'
with open(deb_path, 'r', encoding='utf-8') as f:
    deb_content = f.read()
deb_content = deb_content.replace('@click="fetchDebtors"', '@click="() => fetchDebtors()"')
with open(deb_path, 'w', encoding='utf-8') as f:
    f.write(deb_content)
print("Fixed Debtors.vue")

# 3. Output.vue: filterDateRange type fix
out_path = '/home/xasanboy/ERP/Front/src/views/StaffHR/Output.vue'
with open(out_path, 'r', encoding='utf-8') as f:
    out_content = f.read()
out_content = out_content.replace("const filterDateRange = ref<[string, string] | null>(null)", "const filterDateRange = ref<any>(null)")
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(out_content)
print("Fixed Output.vue")

# 4. PersonalCenter.vue: email property
pc_path = '/home/xasanboy/ERP/Front/src/views/Personal/PersonalCenter/PersonalCenter.vue'
with open(pc_path, 'r', encoding='utf-8') as f:
    pc_content = f.read()
pc_content = pc_content.replace("email: u?.email || '',", "email: (u as any)?.email || '',")
with open(pc_path, 'w', encoding='utf-8') as f:
    f.write(pc_content)
print("Fixed PersonalCenter.vue")

# 5. ConnectedDevices.vue: pair_code property
cd_path = '/home/xasanboy/ERP/Front/src/views/Personal/PersonalCenter/components/ConnectedDevices.vue'
with open(cd_path, 'r', encoding='utf-8') as f:
    cd_content = f.read()
cd_content = cd_content.replace("const pairCode = res.data.pair_code || res.pair_code", "const pairCode = res.data?.pair_code || (res as any)?.pair_code")
cd_content = cd_content.replace("token: res.data.token || res.token,", "token: res.data?.token || (res as any)?.token,")
with open(cd_path, 'w', encoding='utf-8') as f:
    f.write(cd_content)
print("Fixed ConnectedDevices.vue")
