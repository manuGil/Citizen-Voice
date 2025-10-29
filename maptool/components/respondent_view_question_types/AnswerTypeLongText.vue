<template>
    <div class="text-input-wrapper">
      <v-textarea
        label="Your answer"
        variant="outlined"
        v-model="localText"
        @input="updateAnswer"
      >
        <!-- call event every time user types in the input field  -->
      </v-textarea>
    </div>
                <!-- :value should be props.answer.text -->
  <!--  @input="onInput"-->
  </template>


  <script>
  export default {
    name: "AnswerTypeText",
  }
  </script>
  
  <script setup>
  import { ref, watch } from 'vue'
  
  const emit = defineEmits(['updateAnswer']) // always sends the event to the parent component
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
    emit('updateAnswer', localText.value, props.question_index) // emits event with text value only
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
