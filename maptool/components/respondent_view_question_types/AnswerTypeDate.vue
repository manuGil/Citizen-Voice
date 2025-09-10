<template>
  <v-text-field
    v-model="localDate"
    @input="updateAnswer"
    type="date" 
    label="Date"
    clearable
    >
  </v-text-field>
</template>

<script>
export default {
  name: "AnswerTypeDate",
}
</script>

<script setup>
import { ref, watch } from 'vue'

const emit = defineEmits(['updateAnswer'])
const props = defineProps({
  question_index: Number,
  question: Object,
  answer: Object,
})

// Local reactive state for the date input
const localDate = ref(props.answer?.text || '')

// Watch for external changes to props.answer.text and sync locally
watch(() => props.answer?.text, (newDate) => {
  if (newDate !== localDate.value) {
    localDate.value = newDate || ''
  }
}, { immediate: true })

function updateAnswer() {
  emit('updateAnswer', localDate.value, props.question_index)
}
</script>
<style scoped>
</style>
