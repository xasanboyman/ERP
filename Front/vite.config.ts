import { resolve } from 'path'
import { existsSync, readFileSync } from 'fs'
import { loadEnv } from 'vite'
import type { UserConfig, ConfigEnv } from 'vite'
import Vue from '@vitejs/plugin-vue'
import VueJsx from '@vitejs/plugin-vue-jsx'
import progress from 'vite-plugin-progress'
import EslintPlugin from 'vite-plugin-eslint'
import { ViteEjsPlugin } from 'vite-plugin-ejs'
import { viteMockServe } from 'vite-plugin-mock'
import PurgeIcons from 'vite-plugin-purge-icons'
import ServerUrlCopy from 'vite-plugin-url-copy'
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import { createStyleImportPlugin, ElementPlusResolve } from 'vite-plugin-style-import'
import UnoCSS from 'unocss/vite'
import { visualizer } from 'rollup-plugin-visualizer'
import { compression } from 'vite-plugin-compression2'

// https://vitejs.dev/config/
const root = process.cwd()
const devCertificateDir = resolve(root, 'certs')
const devHttps =
  existsSync(resolve(devCertificateDir, 'localhost-key.pem')) &&
  existsSync(resolve(devCertificateDir, 'localhost.pem'))

function pathResolve(dir: string) {
  return resolve(root, '.', dir)
}

export default ({ command, mode }: ConfigEnv): UserConfig => {
  let env = {} as any
  const isBuild = command === 'build'
  if (!isBuild) {
    env = loadEnv(process.argv[3] === '--mode' ? process.argv[4] : process.argv[3], root)
  } else {
    env = loadEnv(mode, root)
  }
  return {
    base: env.VITE_BASE_PATH,
    plugins: [
      Vue({
        script: {
          // 开启defineModel
          defineModel: true
        }
      }),
      VueJsx(),
      ServerUrlCopy(),
      progress(),
      env.VITE_USE_ALL_ELEMENT_PLUS_STYLE === 'false'
        ? createStyleImportPlugin({
            resolves: [ElementPlusResolve()],
            libs: [
              {
                libraryName: 'element-plus',
                esModule: true,
                resolveStyle: (name) => {
                  if (name === 'click-outside') {
                    return ''
                  }
                  return `element-plus/es/components/${name.replace(/^el-/, '')}/style/css`
                }
              }
            ]
          })
        : undefined,
      !isBuild
        ? EslintPlugin({
            cache: false,
            failOnWarning: false,
            failOnError: false,
            include: ['src/**/*.vue', 'src/**/*.ts', 'src/**/*.tsx'] // 检查的文件
          })
        : undefined,
      VueI18nPlugin({
        runtimeOnly: true,
        compositionOnly: true,
        include: [resolve(__dirname, 'src/locales/**')]
      }),
      createSvgIconsPlugin({
        iconDirs: [pathResolve('src/assets/svgs')],
        symbolId: 'icon-[dir]-[name]',
        svgoOptions: true
      }),
      PurgeIcons(),
      env.VITE_USE_MOCK === 'true'
        ? viteMockServe({
            ignore: /^\_/,
            mockPath: 'mock',
            localEnabled: !isBuild,
            prodEnabled: isBuild,
            injectCode: `
          import { setupProdMockServer } from '../mock/_createProductionServer'

          setupProdMockServer()
          `
          })
        : undefined,
      ViteEjsPlugin({
        title: env.VITE_APP_TITLE
      }),
      UnoCSS(),
      ...(isBuild
        ? [
            compression({
              threshold: 1024,
              deleteOriginalAssets: false
            }),
            compression({
              threshold: 1024,
              algorithm: 'brotliCompress',
              deleteOriginalAssets: false
            })
          ]
        : [])
    ].filter(Boolean) as any,

    css: {
      preprocessorOptions: {
        less: {
          additionalData: '@import "./src/styles/variables.module.less";',
          javascriptEnabled: true
        }
      }
    },
    resolve: {
      extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.less', '.css'],
      alias: [
        {
          find: 'axios',
          replacement: resolve(__dirname, 'node_modules/axios/dist/esm/axios.js')
        },
        {
          find: 'vue-i18n',
          replacement: 'vue-i18n/dist/vue-i18n.cjs.js'
        },
        {
          find: /\@\//,
          replacement: `${pathResolve('src')}/`
        }
      ]
    },
    esbuild: {
      pure: env.VITE_DROP_CONSOLE === 'true' ? ['console.log', 'console.debug'] : undefined,
      drop: env.VITE_DROP_DEBUGGER === 'true' ? ['debugger'] : undefined,
      legalComments: 'none'
    },
    build: {
      target: 'es2020',
      outDir: env.VITE_OUT_DIR || 'dist',
      sourcemap: env.VITE_SOURCEMAP === 'true',
      minify: 'esbuild',
      reportCompressedSize: false,
      rollupOptions: {
        plugins: env.VITE_USE_BUNDLE_ANALYZER === 'true' ? [visualizer()] : undefined,
        // Detailed manual chunking for optimal caching and fast loads
        output: {
          manualChunks(id) {
            if (id.includes('node_modules')) {
              if (id.includes('monaco-editor')) return 'vendor-monaco'
              if (
                id.includes('@zxing') ||
                id.includes('quagga') ||
                id.includes('barcode-detector') ||
                id.includes('qrcode') ||
                id.includes('html5-qrcode')
              ) {
                return 'vendor-barcode'
              }
              if (id.includes('echarts') || id.includes('zrender')) return 'vendor-echarts'
              if (id.includes('wangeditor')) return 'vendor-editor'
              if (id.includes('@iconify/vue') || id.includes('@iconify/iconify')) return 'vendor-icons'
              if (id.includes('xgplayer') || id.includes('cropperjs')) return 'vendor-media'
              if (id.includes('element-plus') || id.includes('@element-plus')) return 'vendor-element'
              if (id.includes('lodash-es')) return 'vendor-lodash'
              if (id.includes('dayjs')) return 'vendor-dayjs'
              if (
                id.includes('vue') ||
                id.includes('pinia') ||
                id.includes('vue-router') ||
                id.includes('vue-i18n') ||
                id.includes('@vueuse')
              ) {
                return 'vendor-vue'
              }
              if (
                id.includes('axios') ||
                id.includes('qs') ||
                id.includes('mitt') ||
                id.includes('nprogress') ||
                id.includes('driver.js')
              ) {
                return 'vendor-utils'
              }
            }
          },
          chunkFileNames: 'assets/[name]-[hash].js',
          entryFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash].[ext]'
        }
      },
      chunkSizeWarningLimit: 2000,
      cssCodeSplit: true,
      cssTarget: ['chrome80', 'safari13.1', 'firefox78']
    },
    server: {
      port: 4000,
      https: devHttps
        ? {
            key: readFileSync(resolve(devCertificateDir, 'localhost-key.pem')),
            cert: readFileSync(resolve(devCertificateDir, 'localhost.pem'))
          }
        : undefined,
      proxy: {
        '/api': {
          target: 'https://xn--dr8haa.uz/oracle/erp-api',
          changeOrigin: true,
          secure: false,
          ws: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        },
        '/uploads': {
          target: 'https://xn--dr8haa.uz/oracle/erp-api',
          changeOrigin: true,
          secure: false
        }
      },
      hmr: {
        overlay: false
      },
      host: '0.0.0.0'
    },
    define: {
      'process.env': {},
      global: 'window'
    },
    optimizeDeps: {
      entries: ['index.html'],
      include: [
        'vue',
        'vue-router',
        'vue-types',
        'pinia',
        'lodash-es',
        'element-plus',
        'element-plus/es',
        'element-plus/es/locale/lang/uz-uz',
        'element-plus/es/locale/lang/en',
        '@iconify/vue',
        '@iconify/iconify',
        '@vueuse/core',
        'axios',
        'echarts',
        'echarts-wordcloud',
        'qrcode',
        '@wangeditor/editor',
        '@wangeditor/editor-for-vue',
        'vue-json-pretty',
        '@zxcvbn-ts/core',
        'dayjs',
        'cropperjs',
        'xgplayer',
        'canvas-confetti',
        'howler'
      ]
    }
  }
}
