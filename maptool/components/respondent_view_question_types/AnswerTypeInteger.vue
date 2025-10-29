<template>
  <div class="number-input-wrapper">
    <v-text-field
      v-model="localInteger"
      @input="updateAnswer"
      @blur="validateInteger"
      hide-details
      single-line
      type="number"
      inputmode="numeric"
      :error="hasError"
      :error-messages="errorMessage"
      placeholder="Enter a whole number"
      class="number-input-field"
    />
  </div>
</template>

<script>
export default {
  name: "AnswerTypeInteger"
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

// Local reactive state for the integer input
const localInteger = ref(props.answer?.text || '')
const hasError = ref(false)
const errorMessage = ref('')

// Watch for external changes to props.answer.text and sync locally
watch(() => props.answer?.text, (newInteger) => {
  if (newInteger !== localInteger.value) {
    localInteger.value = newInteger || ''
  }
}, { immediate: true })

/**
 * Validates that the input is a valid integer
 * @returns {boolean} true if valid integer, false otherwise
 */
function isValidInteger(value) {
  if (value === '' || value === null || value === undefined) {
    return true; // Allow empty values (not required validation)
  }

  const num = Number(value);

  // Check if it's a valid number and if it's an integer (no decimal places)
  if (isNaN(num)) {
    return false;
  }

  return Number.isInteger(num);
}

/**
 * Validates the integer value and displays error messages
 */
function validateInteger() {
  const trimmedValue = String(localInteger.value).trim();

  if (trimmedValue === '') {
    hasError.value = false;
    errorMessage.value = '';
    return;
  }

  if (!isValidInteger(trimmedValue)) {
    hasError.value = true;
    errorMessage.value = 'Please enter a valid whole number (no decimals)';
  } else {
    hasError.value = false;
    errorMessage.value = '';
  }
}

/**
 * Updates the answer with the integer value
 * Emits empty string if invalid, actual integer if valid
 */
function updateAnswer() {
  const trimmedValue = String(localInteger.value).trim();

  // Allow empty input
  if (trimmedValue === '') {
    emit('updateAnswer', '', props.question_index);
    hasError.value = false;
    errorMessage.value = '';
    return;
  }

  if (isValidInteger(trimmedValue)) {
    const integerValue = parseInt(trimmedValue, 10);
    emit('updateAnswer', integerValue, props.question_index);
    hasError.value = false;
    errorMessage.value = '';
  } else {
    hasError.value = true;
    errorMessage.value = 'Please enter a valid whole number (no decimals)';
  }
}
</script>

<style scoped>
.number-input-wrapper {
  display: flex;
  padding: 0 16px;
  max-width: 100%;
}

.number-input-field {
  width: 100%;
  max-width: 300px;
}

/* Responsive design for smaller screens */
@media (max-width: 768px) {
  .number-input-field {
    max-width: 250px;
  }
}

@media (max-width: 480px) {
  .number-input-field {
    max-width: 100%;
  }
}
</style>
