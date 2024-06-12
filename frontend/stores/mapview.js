/**
 * This to store the mapview data of an Answer in a Response
 * 
 */

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
        getGeometries: (state) => state.geometries,
        getZoomLevel: (state) => state.zoomLevel,
        getCenter: (state) => state.center,
        getMapServiceUrl: (state) => state.mapServiceUrl,
        getFormattedBody: (state) => {
            return {
                name: state.name,
                map_service_url: state.mapServiceUrl,
                options: {
                    zoom: state.zoomLevel,
                    center: state.center
                },
                geometries: state.geometries
            }
        }
    },
    actions: {
        updateGeometries(geometries) {
            this.geometries = geometries
        },
        updateZoomLevel(zoomLevel) {
            this.zoomLevel = zoomLevel
        },
        updateCenter(center) {
            this.center = center
        },
        updateMapServiceUrl(mapServiceUrl) {
            this.mapServiceUrl = mapServiceUrl
        },
        async createMapview() {
            /**
             * Create a new mapview in the backend with the current state of the store
             */

            var location_url;
            // create the location collection, if there are geometries
            if (Object.keys(this.geometries).length !== 0) {
                const {data: res, error } = await useAsyncData( () => $cmsApi(`/locations/`, setRequestConfig({ method: 'POST', body: {
                    'name': this.name, 
                    'description': null } 
                    }
                )));
                
                location_url = res.value.url
                if (error.value) {
                    throw new Error('Error creating location collection //> ', error.value)
                }
            } else {
                location_url = null
            };

            const global = useGlobalStore()
            const config = setRequestConfig({ method: 'POST', body: this.getFormattedBody })
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
        async updateMapview(mapview_url) {
            const global = useGlobalStore()
            console.log('mapview url at store //> ', mapview_url)
            const config = setRequestConfig({ method: 'PATCH', body: this.getFormattedBody })
            const { data, error, refresh } = await useAsyncData( () => $cmsApi(`${mapview_url}`, config));

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
            global.succes('Map has been updated')
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
            };
            if (error.value) {
                throw new Error('Error fetching map view //> ', error.value)
            };
            return res
        }
    },

})