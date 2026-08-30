import { getSql } from '../_db.js';
import { authenticate } from '../_auth.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const user = authenticate(req, res);
  if (!user) return;

  try {
    const sql = getSql();
    const [salesRows, products, workers, salariesPaid] = await Promise.all([
      sql`SELECT sum(total) as sales_total FROM sales`,
      sql`SELECT * FROM products`,
      sql`SELECT * FROM workers WHERE status = 1`,
      sql`SELECT sum(netSalary) as salaries_paid FROM salaries WHERE status = 'paid'`
    ]);

    const salesTotal = parseFloat(salesRows[0]?.sales_total || 0);
    const totalInventoryRetail = products.reduce((acc, p) => acc + (parseFloat(p.price || 0) * (parseInt(p.quantityInStock || 0, 10))), 0);
    const totalInventoryCost = products.reduce((acc, p) => acc + (parseFloat(p.cost || 0) * (parseInt(p.quantityInStock || 0, 10))), 0);
    const costRatio = totalInventoryRetail > 0 ? (totalInventoryCost / totalInventoryRetail) : 0.65;

    const grossRevenue = salesTotal > 0 ? salesTotal : totalInventoryRetail;
    const cogs = salesTotal > 0 ? (grossRevenue * costRatio) : totalInventoryCost;

    let staffSalaries = parseFloat(salariesPaid[0]?.salaries_paid || 0);
    if (staffSalaries === 0) {
      staffSalaries = workers.reduce((acc, w) => acc + parseFloat(w.baseSalary || 0), 0);
    }

    const shortTermOutputs = 0;
    const totalPayroll = staffSalaries + shortTermOutputs;
    const totalExpenses = cogs + totalPayroll;
    const realNetProfit = grossRevenue - totalExpenses;
    const profitMargin = grossRevenue > 0 ? ((realNetProfit / grossRevenue) * 100) : 0;

    return res.status(200).json({
      code: 0,
      data: {
        grossRevenue: Math.round(grossRevenue * 100) / 100,
        cogs: Math.round(cogs * 100) / 100,
        staffSalaries: Math.round(staffSalaries * 100) / 100,
        shortTermOutputs: Math.round(shortTermOutputs * 100) / 100,
        totalPayroll: Math.round(totalPayroll * 100) / 100,
        totalExpenses: Math.round(totalExpenses * 100) / 100,
        realNetProfit: Math.round(realNetProfit * 100) / 100,
        profitMargin: Math.round(profitMargin * 10) / 10,
        activeWorkersCount: workers.length,
        shortTermTasksCount: 0,
        monthlyFinancials: [],
        expenseBreakdown: [
          { name: "Mahsulot Tannarxi (COGS)", value: Math.round(cogs * 100) / 100 },
          { name: "Doimiy Xodimlar Maoshi", value: Math.round(staffSalaries * 100) / 100 }
        ]
      }
    });
  } catch (err) {
    return res.status(500).json({ error: 'Financial Overview Error', message: err.message });
  }
}
