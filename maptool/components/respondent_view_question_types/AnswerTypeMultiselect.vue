<template>
    <v-container fluid>
      <v-checkbox v-for="(choice, index) in choicesRef"
        :key="index"
        v-model="selected"
        :label="choice"
        :value="index"
        @update:modelValue="updateAnswer"
      ></v-checkbox>
    </v-container>
  </template>
  
  <script>
  export default {
    name: "AnswerTypeSelectMultiple",
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

  const choicesRef = ref(props.question.choices.split(','))
  
  // Parse existing answer to get selected indices
  const getSelectedIndices = () => {
    if (!props.answer?.text) return []
    const selectedChoices = props.answer.text.split(',')
    return choicesRef.value.map((choice, index) => 
      selectedChoices.some(selected => selected.trim() === choice.trim()) ? index : null
    ).filter(index => index !== null)
  }
  
  // Local reactive state for selected checkboxes
  const selected = ref(getSelectedIndices())
  
  // Watch for external changes to props.answer.text and sync locally
  watch(() => props.answer?.text, (newText) => {
    const newIndices = getSelectedIndices()
    if (JSON.stringify(newIndices) !== JSON.stringify(selected.value)) {
      selected.value = newIndices
    }
  }, { immediate: true })
  
  function updateAnswer() {
    const selectedText = selected.value.map(index => choicesRef.value[index]).join(',').trim()
    emit('updateAnswer', selectedText, props.question_index)
  }
  </script>
  <style scoped>
  </style>
  