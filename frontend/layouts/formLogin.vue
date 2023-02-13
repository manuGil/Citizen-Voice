<template>
  <div class="q-pa-md custom-login-form">

    <q-form
      @submit="onSubmit"
      @reset="onReset"
      class="q-gutter-md"
    >
      <q-input
        filled
        v-model="name"
        label="Email *"
        lazy-rules
        :rules="[ val => val && val.length > 0 || 'Please type something']"
      />

      <q-input
        filled
        v-model="password"
        label="Password *"
        lazy-rules
        :rules="[
          val => val !== null && val !== '' || 'Please enter your password'
        ]"
      />

      <!--      <q-toggle v-model="accept" label="I accept the license and terms" />-->

      <!--      <div>-->
      <!--        <q-btn label="Submit" type="submit" color="primary"/>-->
      <!--        <q-btn label="Reset" type="reset" color="primary" flat class="q-ml-sm" />-->
      <!--      </div>-->
    </q-form>
    <q-btn color="white" text-color="black" label="Login" />
  </div>
</template>

<script>
import BaseButton from "../components/BaseButton";
export default {
  name: "formLogin",
  components: {BaseButton}
}
</script>

<style scoped>
.custom-login-form {
  width: 33%;
  min-width: 100px;
}
</style>
