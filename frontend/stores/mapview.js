import { defineStore, } from 'pinia'
import setRequestConfig from './utils/setRequestConfig';
import { useGlobalStore } from './global'

export const useMapViewStore = defineStore('mapView', {
    state: () => ({
        mapViewId: null,
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
            const { data, error, refresh } = await useAsyncData(() => $cmsApi(`/api/map_views/`, config));

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.warning(warnMessage)
                return null

            }
            // Notification
            global.succes('Map saved')
            return { data: data?.value, refresh }
        },
        async updateMapview(id, mapSettings) {
            const global = useGlobalStore()
            const config = setRequestConfig({ method: 'PATCH', body: mapSettings })
            const { data, error, refresh } = await useAsyncData(() => $cmsApi(`/api/map_views/${id}/`, config));

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error._value.data)) {
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
        async fetchMapView(id) {
            console.log('Map_view id //> ', id)
            const config = setRequestConfig({ method: 'GET' })
            const {data: res, error } = await useAsyncData( () => $cmsApi(`${id}`, config));

             console.log('Map_view res //> ', res)
            if (res?.value) {
                this.mapViewId = res.value.id;
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