<template>
    <ClientOnly>
        <q-layout view="hHh lpR fFf">

            <q-header elevated class="bg-primary text-white" height-hint="98">
                <q-toolbar>
                    <q-btn dense flat round icon="menu" @click="toggleLeftDrawer" />

                    <q-toolbar-title>
                        <img class="full-height q-py-sm" height="30" width="100" src="~/assets/icons/civo-logo.svg">
                    </q-toolbar-title>
                </q-toolbar>

                <q-tabs align="left">
                    <q-route-tab to="/page1" label="Page One" />
                    <q-route-tab to="/page2" label="Page Two" />
                    <q-route-tab to="/page3" label="Page Three" />
                </q-tabs>
            </q-header>

            <q-drawer show-if-above v-model="leftDrawerOpen" side="left" bordered>
                <!-- drawer content -->
            </q-drawer>

            <q-page-container>
                <q-page padding>
                    <slot />
                </q-page>
            </q-page-container>

            <q-footer elevated class="bg-grey-8 text-white">
                <q-toolbar>
                    <q-toolbar-title>
                        <img class="full-height q-py-sm" height="30" width="100" src="~/assets/icons/civo-logo.svg">
                        <div>Title</div>
                    </q-toolbar-title>
                </q-toolbar>
            </q-footer>

        </q-layout>
    </ClientOnly>
</template>

<script>
import { ref } from 'vue'

export default {
    setup() {
        const leftDrawerOpen = ref(false)
        const rightDrawerOpen = ref(false)

        return {
            leftDrawerOpen,
            toggleLeftDrawer() {
                leftDrawerOpen.value = !leftDrawerOpen.value
            },

        }
    }
}
</script>

<style lang="scss" scoped>

</style>