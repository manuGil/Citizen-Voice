<template>
    <div class="text-input-wrapper">
      <v-textarea
        rows="1"
        label="Your answer"
        variant="outlined"
        v-model="localText"
        @input="updateAnswer"
      >
      </v-textarea>
    </div>
                <!-- :value should be props.answer.text -->
  <!--  @input="onInput"-->
  </template>
  
  <script>
  export default {
    name: "AnswerTypeShortText",
  }
  </script>
  
  <script setup>
  import { ref, watch } from 'vue'
  
  const emit = defineEmits(['updateAnswer'])
  const props = defineProps({
    question_index: Number,
    question: Object,
    answer: Object
  })

  // Local reactive state for the input
  const localText = ref(props.answer.text || '')

  // Watch for external changes to props.answer.text and sync locally
  watch(() => props.answer.text, (newText) => {
    if (newText !== localText.value) {
      localText.value = newText
    }
  }, { immediate: true })

  function updateAnswer() {
    emit('updateAnswer', localText.value, props.question_index)
  }
  // const answer = ref("")
  //
  // function onInput(e) {
  //   answer.value = e.target.value
  // }
  </script>
  <style scoped>
  .text-input-wrapper {
    padding: 0 16px;
  }
  </style>
