<template>
    <v-text-field
      v-model="localNumber"
      @input="updateAnswer"
      hide-details
      single-line
      type="number"
    />
  </template>
  
  <script>
  export default {
    name: "AnswerTypeInteger"
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
  
  // Local reactive state for the number input
  const localNumber = ref(props.answer?.text || '')
  
  // Watch for external changes to props.answer.text and sync locally
  watch(() => props.answer?.text, (newNumber) => {
    if (newNumber !== localNumber.value) {
      localNumber.value = newNumber || ''
    }
  }, { immediate: true })
  
  function updateAnswer() {
    const numericValue = +localNumber.value; // force conversion to integer or float
    emit('updateAnswer', numericValue, props.question_index);
  }
  </script>
  <style scoped>
  </style>