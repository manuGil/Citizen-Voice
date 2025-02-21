<template>
  <NuxtPage />
  <div class="landingpage-container">
    <div class="landingpage-landingpage">
      <div class="landingpage-topsection">
        <div class="landingpage-header">
          <img
            alt="logoblack1I222"
            src="/external/logoblack1i222-k4fi-200h.png"
            class="landingpage-logoblack11"
          />
          <div class="landingpage-tabs">
            <button class="landingpage-menubutton10">
              <span class="landingpage-text10 Text">About</span>
            </button>
            <button class="landingpage-menubutton11">
              <span class="landingpage-text11 Text">Tools</span>
            </button>
            <button class="landingpage-menubutton12">
              <span class="landingpage-text12 Text">Projects</span>
            </button>
            <button class="landingpage-menubutton13">
              <span class="landingpage-text13 Text">News</span>
            </button>
            <button class="landingpage-menubutton14">
              <span class="landingpage-text14 Text">Research</span>
            </button>
            <button class="landingpage-menubutton15">
              <span class="landingpage-text15 Text">People</span>
            </button>
          </div>
        </div>
        <div class="landingpage-hero">
          <span class="landingpage-text16 MainTitles">Citizen Voice</span>
          <span class="landingpage-text17 Text">
            Citizen Voice aims to empower communities for inclusive and meaningful
            participation in urban planning and design. Advocating for situated
            engagement approaches over one-size-fits-all solutions, Citizen Voice
            develops creative transdisciplinary methods and tools to capture
            perspectives often overlooked in traditional urban data.
          </span>
          <button class="landingpage-button1">
            <span class="landingpage-text18 Smalltitles">Read more</span>
          </button>
        </div>
      </div>
      <div class="landingpage-projects">
        <span class="landingpage-text19 SectionTitles">Projects</span>
        <div class="landingpage-cm-c">
          <div class="landingpage-picture1">
            <img
              alt="pastedImage"
              src="/external/pastedimage-rroh-400h.png"
              class="landingpage-pasted-image1"
            />
          </div>
          <span class="landingpage-text20 Smalltitles">
            Citizens meet Climate
          </span>
        </div>
        <div class="landingpage-bio-ci-vo">
          <div class="landingpage-picture2">
            <img
              alt="pastedImage"
              src="/external/pastedimage-vr28-300h.png"
              class="landingpage-pasted-image2"
            />
          </div>
          <span class="landingpage-text21 Smalltitles">BIO-CiVo</span>
        </div>
        <div class="landingpage-particip-a-ite">
          <div class="landingpage-picture3">
            <img
              alt="pastedImage"
              src="/external/pastedimage-hds-300h.png"
              class="landingpage-pasted-image3"
            />
          </div>
          <span class="landingpage-text22 Smalltitles">ParticipAIte</span>
        </div>
        <div class="landingpage-frame61">
          <button class="landingpage-button2">
            <span class="landingpage-text23 Smalltitles">All the projects</span>
          </button>
        </div>
      </div>
      <div class="landingpage-research">
        <span class="landingpage-text24 SectionTitles">Tools</span>
        <span class="landingpage-text25 Text">
          Part of our research consists of developing and testing tools. All our
          tools are open-source for anyone who wants to try them.
          <span v-html="rawmo9m"></span>
        </span>
        <button class="landingpage-button3">
          <span class="landingpage-text26 Smalltitles">Discover more</span>
        </button>
      </div>
      <div class="landingpage-news">
        <span class="landingpage-text27 SectionTitles">News</span>
        <div class="landingpage-lentefeest">
          <div class="landingpage-picture4"></div>
          <span class="landingpage-text28 Smalltitles">Lentefeest</span>
        </div>
        <div class="landingpage-talk">
          <div class="landingpage-picture5"></div>
          <span class="landingpage-text29 Smalltitles">
            Talk: Empowering Citizen Participation in Climate Action with digital
            platforms
          </span>
        </div>
        <div class="landingpage-ams">
          <div class="landingpage-picture6"></div>
          <span class="landingpage-text30 Smalltitles">
            <span>AMS Institute Scientific</span>
            <br />
            <span>Conference</span>
          </span>
        </div>
        <div class="landingpage-frame62">
          <button class="landingpage-button4">
            <span class="landingpage-text34 Smalltitles">All the news</span>
          </button>
        </div>
      </div>
      <div class="landingpage-footer">
        <img
          alt="logoblack1I334"
          src="/external/logoblack1i334-54w-200h.png"
          class="landingpage-logoblack12"
        />
        <div class="landingpage-linksforfooter">
          <span class="landingpage-text35 Smalltitles">More info</span>
          <button class="landingpage-menubutton16">
            <span class="landingpage-text36 Text">About</span>
          </button>
          <button class="landingpage-menubutton17">
            <span class="landingpage-text37 Text">Tools</span>
          </button>
          <button class="landingpage-menubutton18">
            <span class="landingpage-text38 Text">Projects</span>
          </button>
          <button class="landingpage-menubutton19">
            <span class="landingpage-text39 Text">News</span>
          </button>
          <button class="landingpage-menubutton20">
            <span class="landingpage-text40 Text">Research</span>
          </button>
          <button class="landingpage-menubutton21">
            <span class="landingpage-text41 Text">People</span>
          </button>
        </div>
        <img
          alt="TUDelftlogodescriptorrgb1I334"
          src="/external/tudelftlogodescriptorrgb1i334-ma5-200h.png"
          class="landingpage-tu-delftlogodescriptorrgb1"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Landingpage',
  data() {
    return {
      rawmo9m: ' ',
    }
  },
  head: {
    title: 'exported project',
  },
}
</script>

<style scoped>
.landingpage-container {
  width: 100%;
  display: flex;
  overflow: auto;
  min-height: 100vh;
  align-items: center;
  flex-direction: column;
}
 
.landingpage-landingpage {
  width: 100%;
  height: auto;
  display: flex;
  overflow: hidden;
  align-items: center;
  flex-shrink: 0;
  flex-direction: column;
  background-color: var(--dl-color-default-white);
}
 
.landingpage-topsection {
  gap: 10px;
  height: 680px;
  display: flex;
  overflow: hidden;
  position: relative;
  align-self: stretch;
  align-items: flex-start;
  flex-shrink: 0;
  flex-direction: column;
  background-color: var(--dl-color-default-white);
}
 
.landingpage-header {
  gap: 685px;
  display: flex;
  padding: 15px 64px;
  align-self: stretch;
  align-items: center;
  flex-shrink: 0;
  justify-content: center;
  background-color: var(--dl-color-default-civored);
}
 
.landingpage-logoblack11 {
  width: 133px;
  height: 42px;
}
 
.landingpage-tabs {
  gap: 32px;
  display: flex;
  padding: 3px;
  overflow: hidden;
  flex-grow: 1;
  align-items: center;
  justify-content: space-between;
}
 
.landingpage-menubutton10 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text10 {
  color: var(--dl-color-default-white);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-menubutton11 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text11 {
  color: var(--dl-color-default-white);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-menubutton12 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text12 {
  color: var(--dl-color-default-white);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-menubutton13 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text13 {
  color: var(--dl-color-default-white);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-menubutton14 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text14 {
  color: var(--dl-color-default-white);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-menubutton15 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text15 {
  color: var(--dl-color-default-white);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-hero {
  gap: 16px;
  width: 1438px;
  height: 608px;
  display: flex;
  padding: 80px 160px;
  z-index: 1;
  overflow: hidden;
  align-items: flex-start;
  flex-shrink: 0;
  flex-direction: column;
  justify-content: flex-end;
}
 
.landingpage-text16 {
  color: var(--dl-color-default-black);
  height: auto;
  text-align: left;
  line-height: 80px;
}
 
.landingpage-text17 {
  color: var(--dl-color-default-black);
  height: auto;
  text-align: left;
  line-height: 20px;
}
 
.landingpage-button1 {
  display: flex;
  padding: 8px 16px;
  align-items: center;
  border-radius: 24px;
  justify-content: center;
  background-color: var(--dl-color-default-civodarkgreen);
}
 
.landingpage-text18 {
  color: var(--dl-color-default-white);
  height: auto;
  text-align: center;
  line-height: 24px;
}
 
.landingpage-projects {
  gap: 32px;
  display: flex;
  padding: 80px 160px;
  overflow: hidden;
  flex-wrap: wrap;
  align-self: stretch;
  align-items: flex-start;
  flex-shrink: 0;
  border-radius: 40px 40px 0 0;
  justify-content: space-between;
  background-color: var(--dl-color-default-civomediumgrey);
}
 
.landingpage-text19 {
  color: var(--dl-color-default-black);
  width: 1117px;
  height: auto;
  text-align: left;
  line-height: 44px;
}
 
.landingpage-cm-c {
  gap: 16px;
  width: 332px;
  height: 372px;
  display: flex;
  padding: 16px;
  overflow: hidden;
  align-items: flex-start;
  flex-shrink: 0;
  border-radius: 16px;
  flex-direction: column;
  justify-content: center;
  background-color: var(--dl-color-default-white);
}
 
.landingpage-picture1 {
  gap: 10px;
  width: 300px;
  height: 300px;
  display: flex;
  padding: 10px;
  position: relative;
  flex-grow: 1;
  align-self: stretch;
  align-items: center;
  border-radius: 8px;
  justify-content: center;
}
 
.landingpage-pasted-image1 {
  width: 313px;
  height: 310px;
}
 
.landingpage-text20 {
  color: var(--dl-color-default-civored);
  height: auto;
  text-align: center;
  line-height: 24px;
}
 
.landingpage-bio-ci-vo {
  gap: 16px;
  width: 332px;
  height: 372px;
  display: flex;
  padding: 16px;
  overflow: hidden;
  align-items: flex-start;
  flex-shrink: 0;
  border-radius: 16px;
  flex-direction: column;
  justify-content: center;
  background-color: var(--dl-color-default-white);
}
 
.landingpage-picture2 {
  gap: 10px;
  width: 300px;
  height: 300px;
  display: flex;
  padding: 10px;
  position: relative;
  flex-grow: 1;
  align-self: stretch;
  align-items: flex-start;
  border-radius: 8px;
}
 
.landingpage-pasted-image2 {
  width: 286px;
  height: 100%;
}
 
.landingpage-text21 {
  color: var(--dl-color-default-civored);
  height: auto;
  text-align: center;
  line-height: 24px;
}
 
.landingpage-particip-a-ite {
  gap: 16px;
  width: 332px;
  height: 372px;
  display: flex;
  padding: 16px;
  overflow: hidden;
  align-items: flex-start;
  flex-shrink: 0;
  border-radius: 16px;
  flex-direction: column;
  justify-content: center;
  background-color: var(--dl-color-default-white);
}
 
.landingpage-picture3 {
  gap: 10px;
  width: 300px;
  height: 300px;
  display: flex;
  padding: 10px;
  position: relative;
  flex-grow: 1;
  align-self: stretch;
  align-items: flex-start;
  border-radius: 8px;
}
 
.landingpage-pasted-image3 {
  width: 100%;
  height: 100%;
}
 
.landingpage-text22 {
  color: var(--dl-color-default-civored);
  height: auto;
  text-align: center;
  line-height: 24px;
}
 
.landingpage-frame61 {
  width: 1117px;
  height: 40px;
  display: flex;
  overflow: hidden;
  align-items: center;
  flex-shrink: 0;
  flex-direction: column;
}
 
.landingpage-button2 {
  display: flex;
  padding: 8px 16px;
  align-items: center;
  border-radius: 24px;
  justify-content: center;
  background-color: var(--dl-color-default-civoblue);
}
 
.landingpage-text23 {
  color: var(--dl-color-default-white);
  height: auto;
  text-align: center;
  line-height: 24px;
}
 
.landingpage-research {
  gap: 16px;
  display: flex;
  padding: 80px 160px;
  overflow: hidden;
  align-self: stretch;
  align-items: flex-start;
  flex-direction: column;
  justify-content: flex-end;
}
 
.landingpage-text24 {
  color: var(--dl-color-default-black);
  height: auto;
  align-self: stretch;
  text-align: left;
  line-height: 44px;
}
 
.landingpage-text25 {
  color: var(--dl-color-default-black);
  width: 608px;
  height: auto;
  text-align: left;
  line-height: 20px;
}
 
.landingpage-button3 {
  display: flex;
  padding: 8px 16px;
  align-items: center;
  border-radius: 24px;
  justify-content: center;
  background-color: var(--dl-color-default-civodarkgreen);
}
 
.landingpage-text26 {
  color: var(--dl-color-default-white);
  height: auto;
  text-align: center;
  line-height: 24px;
}
 
.landingpage-news {
  gap: 32px;
  display: flex;
  padding: 80px 160px;
  overflow: hidden;
  flex-wrap: wrap;
  align-self: stretch;
  align-items: flex-start;
  flex-shrink: 0;
  justify-content: space-between;
  background-color: var(--dl-color-default-civomediumgrey);
}
 
.landingpage-text27 {
  color: var(--dl-color-default-black);
  width: 1117px;
  height: auto;
  text-align: left;
  line-height: 44px;
}
 
.landingpage-lentefeest {
  gap: 16px;
  width: 332px;
  height: 372px;
  display: flex;
  padding: 16px;
  overflow: hidden;
  align-items: flex-start;
  flex-shrink: 0;
  border-radius: 16px;
  flex-direction: column;
  justify-content: center;
  background-color: var(--dl-color-default-white);
}
 
.landingpage-picture4 {
  gap: 10px;
  width: 300px;
  height: 300px;
  display: flex;
  padding: 10px;
  position: relative;
  flex-grow: 1;
  align-self: stretch;
  align-items: flex-start;
  border-radius: 8px;
}
 
.landingpage-text28 {
  color: var(--dl-color-default-civored);
  height: auto;
  text-align: center;
  line-height: 24px;
}
 
.landingpage-talk {
  gap: 16px;
  width: 332px;
  height: 372px;
  display: flex;
  padding: 16px;
  overflow: hidden;
  align-items: flex-start;
  flex-shrink: 0;
  border-radius: 16px;
  flex-direction: column;
  justify-content: center;
  background-color: var(--dl-color-default-white);
}
 
.landingpage-picture5 {
  gap: 10px;
  width: 300px;
  height: 228px;
  display: flex;
  padding: 10px;
  position: relative;
  flex-grow: 1;
  align-self: stretch;
  align-items: flex-start;
  border-radius: 8px;
}
 
.landingpage-text29 {
  color: var(--dl-color-default-civored);
  width: 308px;
  height: auto;
  text-align: left;
  line-height: 24px;
}
 
.landingpage-ams {
  gap: 16px;
  width: 332px;
  height: 372px;
  display: flex;
  padding: 16px;
  overflow: hidden;
  align-items: flex-start;
  flex-shrink: 0;
  border-radius: 16px;
  flex-direction: column;
  justify-content: center;
  background-color: var(--dl-color-default-white);
}
 
.landingpage-picture6 {
  gap: 10px;
  width: 300px;
  height: 276px;
  display: flex;
  padding: 10px;
  position: relative;
  flex-grow: 1;
  align-self: stretch;
  align-items: flex-start;
  border-radius: 8px;
}
 
.landingpage-text30 {
  color: var(--dl-color-default-civored);
  height: auto;
  text-align: left;
  line-height: 24px;
}
 
.landingpage-frame62 {
  width: 1117px;
  height: 40px;
  display: flex;
  overflow: hidden;
  align-items: center;
  flex-shrink: 0;
  flex-direction: column;
}
 
.landingpage-button4 {
  display: flex;
  padding: 8px 16px;
  align-items: center;
  border-radius: 24px;
  justify-content: center;
  background-color: var(--dl-color-default-civoblue);
}
 
.landingpage-text34 {
  color: var(--dl-color-default-white);
  height: auto;
  text-align: center;
  line-height: 24px;
}
 
.landingpage-footer {
  gap: 32px;
  display: flex;
  padding: 40px 64px;
  overflow: hidden;
  align-self: stretch;
  align-items: flex-start;
  flex-shrink: 0;
  justify-content: space-between;
  background-color: var(--dl-color-default-civolightgrey);
}
 
.landingpage-logoblack12 {
  width: 196px;
  height: 62px;
}
 
.landingpage-linksforfooter {
  gap: 8px;
  display: flex;
  overflow: hidden;
  align-items: center;
  flex-direction: column;
}
 
.landingpage-text35 {
  color: var(--dl-color-default-black);
  height: auto;
  text-align: center;
  line-height: 24px;
}
 
.landingpage-menubutton16 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text36 {
  color: var(--dl-color-default-black);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-menubutton17 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text37 {
  color: var(--dl-color-default-black);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-menubutton18 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text38 {
  color: var(--dl-color-default-black);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-menubutton19 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text39 {
  color: var(--dl-color-default-black);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-menubutton20 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text40 {
  color: var(--dl-color-default-black);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-menubutton21 {
  gap: 30px;
  height: 20px;
  display: flex;
  overflow: hidden;
  align-items: flex-end;
  flex-shrink: 0;
  justify-content: center;
}
 
.landingpage-text41 {
  color: var(--dl-color-default-black);
  height: auto;
  text-align: center;
  line-height: 20px;
}
 
.landingpage-tu-delftlogodescriptorrgb1 {
  width: 220px;
  height: 62px;
}
</style>
