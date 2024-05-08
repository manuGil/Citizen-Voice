import { defineStore, } from 'pinia'
import setRequestConfig from './utils/setRequestConfig';
import { useGlobalStore } from './global'

export const useMapViewStore = defineStore('mapView', {
    state: () => ({
        id: null,
        url: null,
        name: null,
        mapServiceUrl: null,
        zoomLevel: null,
        center: null,
        geometries: {} // a GeoJSON featurecollection for all geometries
    }),
    getters: {
        // getCurrentQuestions: (state) => state.currentQuestions
        getGeometries: (state) => state.geometries
    },
    actions: {
        async createMapview(mapSettings) {
            const global = useGlobalStore()
            const config = setRequestConfig({ method: 'POST', body: mapSettings })
            const { data, error, refresh } = await useAsyncData(() => $cmsApi(`/map_views/`, config));

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error.value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.warning(warnMessage)
                return null
ß
            }
            // Notification
            global.succes('Map saved')
            return { data: data?.value, refresh }
        },
        async updateMapview(mapview_url, mapSettings) {
            const global = useGlobalStore()
            console.log('mapview url at store //> ', mapview_url)
            const config = setRequestConfig({ method: 'PATCH', body: mapSettings })
            const { data, error, refresh } = await useAsyncData( () => $cmsApi(`${mapview_url}`, config));

            // CONTINUE HERE: CHECK why patch is not allowed (the serializers?)
            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error.value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.warning(warnMessage)
                return null

            }
            // Notification
            global.succes('Map update saved')
            return { data: data?.value, refresh }
        },
        async fetchMapView(url) {
            console.log('Map_view id //> ', url)
            const config = setRequestConfig({ method: 'GET' })
            const {data: res, error } = await useAsyncData( () => $cmsApi(`${url}`, config));

             console.log('Map_view res //> ', res)
            if (res?.value) {
                this.id = res.value.id;
                this.url= res.value.url;
                this.name = res.value.name;
                this.mapServiceUrl = res.value.map_service_url;
                console.log('res.value.options.zoom //> ', res.value.options.zoom)
                this.zoomLevel = res.value.options.zoom;
                this.center = res.value.options.center;
                this.geometries = res.value.geometries
            }

            return res
        }
    },

})