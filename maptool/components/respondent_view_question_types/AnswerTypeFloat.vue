<template>
  <div>
    <v-text-field
      v-model="localFloat"
      @input="updateAnswer"
      @blur="validateFloat"
      hide-details
      single-line
      type="number"
      inputmode="decimal"
      step="any"
      :error="hasError"
      :error-messages="errorMessage"
      placeholder="Enter a decimal number"
    />
  </div>
</template>

<script>
export default {
  name: "AnswerTypeFloat"
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

// Local reactive state for the float input
const localFloat = ref(props.answer?.text || '')
const hasError = ref(false)
const errorMessage = ref('')

// Watch for external changes to props.answer.text and sync locally
watch(() => props.answer?.text, (newFloat) => {
  if (newFloat !== localFloat.value) {
    localFloat.value = newFloat || ''
  }
}, { immediate: true })

/**
 * Validates that the input is a valid floating-point number
 * @returns {boolean} true if valid number, false otherwise
 */
function isValidFloat(value) {
  if (value === '' || value === null || value === undefined) {
    return true; // Allow empty values (not required validation)
  }

  const num = Number(value);

  // Check if it's a valid number
  if (isNaN(num)) {
    return false;
  }

  return true; // Any valid number is acceptable (integer or float)
}

/**
 * Validates the float value and displays error messages
 */
function validateFloat() {
  const trimmedValue = String(localFloat.value).trim();

  if (trimmedValue === '') {
    hasError.value = false;
    errorMessage.value = '';
    return;
  }

  if (!isValidFloat(trimmedValue)) {
    hasError.value = true;
    errorMessage.value = 'Please enter a valid decimal number';
  } else {
    hasError.value = false;
    errorMessage.value = '';
  }
}

/**
 * Updates the answer with the float value
 * Emits empty string if invalid, actual float if valid
 */
function updateAnswer() {
  const trimmedValue = String(localFloat.value).trim();

  // Allow empty input
  if (trimmedValue === '') {
    emit('updateAnswer', '', props.question_index);
    hasError.value = false;
    errorMessage.value = '';
    return;
  }

  if (isValidFloat(trimmedValue)) {
    const floatValue = parseFloat(trimmedValue);
    emit('updateAnswer', floatValue, props.question_index);
    hasError.value = false;
    errorMessage.value = '';
  } else {
    hasError.value = true;
    errorMessage.value = 'Please enter a valid decimal number';
  }
}
</script>

<style scoped>
</style>
