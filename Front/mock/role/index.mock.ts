import Mock from 'mockjs'
import { SUCCESS_CODE } from '@/constants'

const adminList = [
  {
    path: '/dashboard',
    component: '#',
    redirect: '/dashboard/analysis',
    name: 'Dashboard',
    meta: {
      title: 'router.dashboard',
      icon: 'vi-ant-design:dashboard-filled',
      alwaysShow: true
    },
    children: [
      {
        path: 'analysis',
        component: 'views/Dashboard/Analysis',
        name: 'Analysis',
        meta: {
          title: 'router.analysis',
          noCache: true,
          affix: true
        }
      },
      {
        path: 'workplace',
        component: 'views/Dashboard/Workplace',
        name: 'Workplace',
        meta: {
          title: 'router.workplace',
          noCache: true,
          affix: true
        }
      }
    ]
  },
  {
    path: '/product',
    component: '#',
    redirect: '/product/list',
    name: 'ProductRoot',
    meta: {
      title: 'Omborxona',
      icon: 'vi-ep:goods',
      alwaysShow: true
    },
    children: [
      {
        path: 'list',
        component: 'views/Product/Product',
        name: 'ProductManagement',
        meta: {
          title: 'Ombor Mahsulotlari',
          noCache: true
        }
      }
    ]
  },
  {
    path: '/sales',
    component: '#',
    redirect: '/sales/pos',
    name: 'SalesRoot',
    meta: {
      title: 'Sotuvlar (POS)',
      icon: 'vi-ep:shopping-cart-full',
      alwaysShow: false
    },
    children: [
      {
        path: 'pos',
        component: 'views/Sales/Pos',
        name: 'SalesPos',
        meta: {
          title: 'Sotuvlar (POS)',
          noCache: true
        }
      }
    ]
  },
  {
    path: '/hr',
    component: '#',
    redirect: '/hr/workers',
    name: 'HRRoot',
    meta: {
      title: 'Xodimlar (Employees)',
      icon: 'vi-ep:avatar',
      alwaysShow: true
    },
    children: [
      {
        path: 'workers',
        component: 'views/Worker/Worker',
        name: 'WorkerManagement',
        meta: {
          title: 'Xodimlar (Employees)',
          noCache: true
        }
      }
    ]
  },
  {
    path: '/authorization',
    component: '#',
    redirect: '/authorization/role',
    name: 'Authorization',
    meta: {
      title: 'Huquqlar & Sozlamalar',
      icon: 'vi-eos-icons:role-binding',
      alwaysShow: true
    },
    children: [
      {
        path: 'department',
        component: 'views/Authorization/Department/Department',
        name: 'Department',
        meta: {
          title: 'Bo\'limlar',
          noCache: true
        }
      },
      {
        path: 'role',
        component: 'views/Authorization/Role/Role',
        name: 'Role',
        meta: {
          title: 'Rollar',
          noCache: true
        }
      }
    ]
  }
]

export default [
  {
    url: '/mock/role/list',
    method: 'get',
    response: () => {
      return {
        code: SUCCESS_CODE,
        data: adminList
      }
    }
  },
  {
    url: '/mock/role/table',
    method: 'get',
    response: () => {
      return {
        code: SUCCESS_CODE,
        data: {
          total: 3,
          list: [
            {
              id: '1',
              roleName: 'Super Administrator',
              status: 1,
              remark: 'Tizimning barcha boshqaruv huquqlariga ega',
              createTime: '2026-07-06 12:00:00'
            },
            {
              id: '2',
              roleName: 'Administrator',
              status: 1,
              remark: 'Oddiy administrator',
              createTime: '2026-07-06 12:00:00'
            },
            {
              id: '3',
              roleName: 'Oddiy xodim',
              status: 1,
              remark: 'Faqat ko\'rish huquqiga ega bo\'lgan xodim',
              createTime: '2026-07-06 12:00:00'
            }
          ]
        }
      }
    }
  }
]
