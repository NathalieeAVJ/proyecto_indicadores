import axios from '@/plugins/axios'

export default {
  getSummaryStats() {
    return axios.get('/api/dashboard/summary/')
  }
}
