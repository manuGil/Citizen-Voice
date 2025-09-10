<template>
    <v-container style="padding: 16px">
      <v-radio-group v-model="selectedOption" @update:modelValue="updateAnswer">
        <v-radio v-for="(option, index) in optionsRef" :key="index" :value="index" :label="option">
        </v-radio>
      </v-radio-group>
    </v-container>
  </template>
  
  <script>
  export default {
    name: "AnswerTypeSelect",
  }
  </script>
  
  <script setup>
  import { ref, watch, computed } from 'vue'
  
  const emit = defineEmits(['updateAnswer'])
  const props = defineProps({
    question_index: Number,
    question: Object,
    answer: Object,
  })
  
  const optionsRef = ref(props.question.choices.split(','))
  
  // Find the index of the current answer
  const getSelectedIndex = () => {
    if (!props.answer?.text) return null
    return optionsRef.value.findIndex(option => option.trim() === props.answer.text)
  }
  
  // Local reactive state for the selected option
  const selectedOption = ref(getSelectedIndex())
  
  // Watch for external changes to props.answer.text and sync locally
  watch(() => props.answer?.text, (newText) => {
    const newIndex = optionsRef.value.findIndex(option => option.trim() === newText)
    if (newIndex !== selectedOption.value) {
      selectedOption.value = newIndex >= 0 ? newIndex : null
    }
  }, { immediate: true })
  
  function updateAnswer() {
    if (selectedOption.value !== null) {
      const selectedText = optionsRef.value[selectedOption.value].trim()
      emit('updateAnswer', selectedText, props.question_index)
    }
  }
  </script>
  <style scoped>
  </style>
  