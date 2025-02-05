/* Theme selector */
function setColorScheme(scheme) {
  console.log("Setting scheme to: ", scheme);
  switch(scheme){
    case 'dark':
      document.documentElement.classList.add('dark')
      break;
    case 'light':
      document.documentElement.classList.remove('dark')
      // Light
      break;
    default:
      // Default
      console.log('default');
      break;
  }
}

const getPreferredScheme = () => window?.matchMedia?.('(prefers-color-scheme:dark)')?.matches ? 'dark' : 'light';
const updateColorScheme = ()=> setColorScheme(getPreferredScheme());

if(window.matchMedia){
  var colorSchemeQuery = window.matchMedia('(prefers-color-scheme: dark)');
  colorSchemeQuery.addEventListener('change', updateColorScheme);
}

updateColorScheme();

/* Icon selector */
const iconSelector = () => {
  return {
    icon: null,
    get mdiIcon() { return `mdi-${this.icon ? this.icon: "border-none-variant"}`; },
  }
}
