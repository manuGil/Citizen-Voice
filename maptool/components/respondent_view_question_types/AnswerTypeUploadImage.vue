<template>
  <v-container style="padding: 16px">
    <div class="image-upload-container">
      <!-- File input -->
      <v-file-input
        ref="fileInput"
        v-model="selectedFile"
        accept="image/*"
        label="Choose an image"
        prepend-icon="mdi-camera"
        show-size
        :rules="fileRules"
      />
      
      <!-- File is automatically stored when selected -->
      
      <!-- Image preview -->
      <div v-if="preview || storedAnswer?.image_url" class="image-preview mt-4">
        <v-card>
          <v-img
            :src="preview || storedAnswer?.image_url"
            alt="Image preview"
            max-height="300"
            contain
          />
          <v-card-actions>
            <v-btn
              v-if="preview || storedAnswer?.image_file"
              @click="removeImage"
              color="error"
              text
              small
            >
              <v-icon left>mdi-delete</v-icon>
              Remove Image
            </v-btn>
          </v-card-actions>
        </v-card>
      </div>
      
      <!-- Error message -->
      <v-alert
        v-if="errorMessage"
        type="error"
        dismissible
        class="mt-2"
        @input="errorMessage = null"
      >
        {{ errorMessage }}
      </v-alert>
      
      <!-- Success message -->
      <v-alert
        v-if="successMessage"
        type="success"
        dismissible
        class="mt-2"
        @input="successMessage = null"
      >
        {{ successMessage }}
      </v-alert>
    </div>
  </v-container>
</template>

<script>
export default {
  name: "ImageUploadAnswer",
}
</script>

<script setup>

import { useSurveyStore } from '~/stores/survey'
import { useResponseStore } from '~/stores/response';
import { en } from 'vuetify/locale';

const surveyStore = useSurveyStore();
const responseStore = useResponseStore();

const router = useRouter();

const emit = defineEmits(['updateAnswer'])
const props = defineProps({
  question_index: Number,
  question: Object,
  answer: Object
})

// Reactive data
const selectedFile = ref(null)
const preview = ref(null)
const errorMessage = ref(null)
const successMessage = ref(null)

// Get stored answer for this question
const storedAnswer = computed(() => {
  return responseStore.getAnswerForQuestion(props.question.url)
})

// File validation rules
const fileRules = [
  value => {
    if (!value) return true

    // Handle both single File object and array of Files from v-file-input
    const file = Array.isArray(value) ? value[0] : value
    if (!file) return true

    if (file.size > 5 * 1024 * 1024) {
      return 'Image size should be less than 5MB'
    }
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      return 'Please select a valid image file (JPEG, PNG, GIF, WebP)'
    }
    return true
  }
]


// Watch for changes to selectedFile (from v-model)
watch(selectedFile, (newFile, oldFile) => {
  console.log('selectedFile changed:', newFile, typeof newFile);

  // If no file selected (cleared), remove stored image
  if (!newFile || (Array.isArray(newFile) && newFile.length === 0)) {
    preview.value = null;
    responseStore.removeAnswerImage(props.question.url);
    emit('updateAnswer', '', props.question_index);

    // Clear any previous alerts when X button is clicked
    errorMessage.value = null;
    successMessage.value = null;

    return;
  }

  // Extract file from array if needed (v-file-input stores as array)
  const file = Array.isArray(newFile) ? newFile[0] : newFile

  // Validate that we have a proper File object
  if (!(file instanceof File)) {
    console.error('Invalid file object:', file);
    preview.value = null;
    responseStore.removeAnswerImage(props.question.url);
    return;
  }
  
  // Validate file first
  const validation = fileRules[0](file);
  if (validation !== true) {
    errorMessage.value = validation;
    preview.value = null;
    responseStore.removeAnswerImage(props.question.url);
    selectedFile.value = null; // Clear the invalid selection
    return;
  }

  console.log('Processing file:', file.name, file.type, file.size);

  // Store file in response store immediately
  responseStore.updateAnswerImage(props.question.url, file);

  // Create preview
  const reader = new FileReader();
  reader.onload = (e) => {
    preview.value = e.target.result;
    successMessage.value = 'Image will be uploaded when survey is submitted!';

    // Emit the updateAnswer event to trigger the parent's handleUpdateAnswer
    emit('updateAnswer', `Image selected: ${file.name}`, props.question_index);
  };
  reader.onerror = (e) => {
    console.error('FileReader error:', e);
    errorMessage.value = 'Failed to read file';
    responseStore.removeAnswerImage(props.question.url);
  };

  reader.readAsDataURL(file);
})



// Remove stored image
function removeImage() {
  try {
    // Remove from store
    responseStore.removeAnswerImage(props.question.url);
    
    // Clear local state
    preview.value = null;
    selectedFile.value = null;
    
    // Emit empty answer to update the response store
    emit('updateAnswer', '', props.question_index);

    // Clear any previous alerts
    errorMessage.value = null;
    successMessage.value = null;
    
    // successMessage.value = 'Image removed successfully!';
    
  } catch (error) {
    console.error('Remove failed:', error);
    errorMessage.value = 'Failed to remove image. Please try again.';
  }
}

// Initialize component with stored data
onMounted(() => {
  const stored = responseStore.getAnswerForQuestion(props.question.url);
  if (stored) {
    if (stored.image_url) {
      // Display already uploaded image
      preview.value = null; // Will show stored.image_url in template
    } else if (stored.image_file) {
      // Recreate preview for selected but not yet uploaded file
      const reader = new FileReader();
      reader.onload = (e) => {
        preview.value = e.target.result;
      };
      reader.readAsDataURL(stored.image_file);
      selectedFile.value = stored.image_file;
    }
  }
})
</script>

<style scoped>
.image-upload-container {
  max-width: 500px;
}

.image-preview {
  border: 2px dashed #ccc;
  border-radius: 4px;
  padding: 16px;
}

.v-file-input {
  margin-bottom: 16px;
}
</style>