<template>
  <div class="date-input-wrapper">
    <v-text-field
      v-model="localDate"
      @input="updateAnswer"
      type="date"
      label="Date"
      clearable
      class="date-input-field"
    >
    </v-text-field>
  </div>
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
.date-input-wrapper {
  display: flex;
  padding: 0 16px;
  max-width: 100%;
}

.date-input-field {
  width: 100%;
  max-width: 300px;
}

/* Responsive design for smaller screens */
@media (max-width: 768px) {
  .date-input-field {
    max-width: 250px;
  }
}

@media (max-width: 480px) {
  .date-input-field {
    max-width: 100%;
  }
}
</style>
