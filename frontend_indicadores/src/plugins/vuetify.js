/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#9575CD', // Morado Pastel
          secondary: '#B39DDB',
          background: '#F3E5F5', // Morado Claro (Lavender)
          surface: '#FFFFFF',
          'on-surface': '#4A148C',
          info: '#81D4FA', // Azul pastel
          success: '#A5D6A7', // Verde pastel
          warning: '#FFF59D', // Amarillo pastel
          error: '#EF9A9A', // Rojo pastel
        },
      },
    },
  },
})
