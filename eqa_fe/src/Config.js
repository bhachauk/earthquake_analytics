// config.js

//dev
export const PROD_API_URL = "http://localhost:3000"
//prod
//export const PROD_API_URL = "https://earthquake-analytics.vercel.app"


export function GetMetricURL(metric) {

    return PROD_API_URL  + "/metrics/"+ metric;
}

