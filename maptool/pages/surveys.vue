<template>
    <NuxtLayout name="default">
            <v-sheet 
                max-width="900px"
                class="d-flex align-center flex-wrap mx-auto px-5">
                <div>
                    <h1 class="text-h1 ">Citizen Mapping Tool</h1>
                </div>
                <div class="text-justify py-5">
                    <p class="text-body-1">
                        The <strong>Citizen Mapping Tool</strong> is an <strong>open source tool</strong> that enable researchers and practitioners to create surveys that include 
                        geospatial questions. Those questions are used to collect information about places citizens
                        are familiar with, or to ask them to select locations on a map.
                    </p>
                    <p class="text-body-1 py-2">
                        The tool is designed to be easy to use and accessible to a wide range of users, including those with 
                        limited technical expertise. It is also designed to be flexible and customizable, allowing users to 
                        tailor the survey to their specific needs. Refer to the <a class="external-link" href="https://citizens-collective.github.io/Citizen-Voice/" target="_blank" rel="noopener">Citizen Voice documentation</a> for more information.
                    </p>

                    <p class="text-body-1 py-2">
                        Answers with geospatial data can be visualize on a dashboard such as <a class="external-link" :href="dashboardLink" target="_blank" rel="noopener">CIVILIAN Dashboard</a>.
                    </p>
                    <p class="text-body-1 py-2">
                        The demos below showcase how this app can be used. <strong> Feel free to explore them!</strong>
                    </p>

                </div>
                <div class="row q-col-gutter-sm">
                    <v-card 
                        v-for="survey in surveys"  
                        :title="survey.name"
                        :subtitle="'Published: ' + formatDate(survey.publishe_date)"
                        variant="elevated"
                        max-width="400"
                        class="civo-card"
                        hover
                        >
                            <v-card-actions>
                                <v-btn @click="selectSurvey(survey.id)" color="primary" variant="elevated">
                                Participate
                                </v-btn>
                            </v-card-actions>
                            <v-divider></v-divider>
                    </v-card>
                </div>
            </v-sheet>
    </NuxtLayout>
</template>
<script setup>
import { formatDate } from "~/utils/formatData"

const surveyStore = useSurveyStore();
surveyStore.$reset(); // reset SelectedSurvey to null

const dashboardLink = `${window.location.origin}/cv-portal/dashboard`;
// const surveys = {};
const {data: surveys} = await surveyStore.getSurveys();
// console.log(surveys);

// sets id on surveyStore and redirects to survey/id page
async function selectSurvey (id) {
    surveyStore.selectSurvey(id);
    await navigateTo(`/survey/${id}`);
};

</script>
<style lang="scss">
.civo-card {
    margin: 20px 15px
}

.padding-16 {
    padding: 16px;
}

// Hyperlink styles
.external-link {
    color: #1976d2; // Material Design primary blue
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s ease;
    
    &:hover {
        color: #1565c0; // Darker blue on hover
        text-decoration: underline;
    }
    
    &:focus {
        outline: 2px solid #1976d2;
        outline-offset: 2px;
        border-radius: 2px;
    }
    
    &:visited {
        color: #7b1fa2; // Purple for visited links
    }
    
    // For external links (with target="_blank")
    &[target="_blank"] {
        &::after {
        content: '';
        display: inline-block;
        width: 0.75em;
        height: 0.75em;
        margin-left: 0em;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%231976d2' d='M6 1h5v5L9.5 4.5 6 8 4 6l3.5-3.5L6 1z'/%3E%3C/svg%3E");
        background-size: contain;
        background-repeat: no-repeat;
        vertical-align: middle;
        }
    }
}
</style>
