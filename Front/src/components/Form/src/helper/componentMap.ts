import { defineAsyncComponent, type Component } from 'vue'
import {
  ElCascader,
  ElCheckboxGroup,
  ElColorPicker,
  ElDatePicker,
  ElInput,
  ElInputNumber,
  ElRadioGroup,
  ElRate,
  ElSelect,
  ElSelectV2,
  ElSlider,
  ElSwitch,
  ElTimePicker,
  ElTimeSelect,
  ElTransfer,
  ElAutocomplete,
  ElDivider,
  ElTreeSelect,
  ElUpload
} from 'element-plus'
import { ComponentName } from '../types'

const InputPassword = defineAsyncComponent(
  () => import('@/components/InputPassword/src/InputPassword.vue')
)
const Editor = defineAsyncComponent(() => import('@/components/Editor/src/Editor.vue'))
const JsonEditor = defineAsyncComponent(() => import('@/components/JsonEditor/src/JsonEditor.vue'))
const IconPicker = defineAsyncComponent(() => import('@/components/IconPicker/src/IconPicker.vue'))
const IAgree = defineAsyncComponent(() => import('@/components/IAgree/src/IAgree.vue'))

const componentMap: Recordable<Component, ComponentName> = {
  RadioGroup: ElRadioGroup,
  RadioButton: ElRadioGroup,
  CheckboxGroup: ElCheckboxGroup,
  CheckboxButton: ElCheckboxGroup,
  Input: ElInput,
  Autocomplete: ElAutocomplete,
  InputNumber: ElInputNumber,
  Select: ElSelect,
  Cascader: ElCascader,
  Switch: ElSwitch,
  Slider: ElSlider,
  TimePicker: ElTimePicker,
  DatePicker: ElDatePicker,
  Rate: ElRate,
  ColorPicker: ElColorPicker,
  Transfer: ElTransfer,
  Divider: ElDivider,
  TimeSelect: ElTimeSelect,
  SelectV2: ElSelectV2,
  InputPassword: InputPassword,
  Editor: Editor,
  TreeSelect: ElTreeSelect,
  Upload: ElUpload,
  JsonEditor: JsonEditor,
  IconPicker: IconPicker,
  IAgree: IAgree
}

export { componentMap }
