let sidebarPostformMsg = document.getElementById('sidebar-postform-msg')
let sidebarPostformBtn = document.getElementById('sidebar-postform-btn')
sidebarPostformMsg.addEventListener('input', () => {
  if (sidebarPostformBtn.disabled && sidebarPostformMsg.value !== "") {
    sidebarPostformBtn.disabled = false;
  } else if ((!sidebarPostformBtn.disabled) && sidebarPostformMsg.value === "") {
    sidebarPostformBtn.disabled = true;
  }
});

let postformMsg = document.getElementById('postform-msg')
let postformBtn = document.getElementById('postform-btn')
postformMsg.addEventListener('input', () => {
  if (postformBtn.disabled && postformMsg.value !== "") {
    postformBtn.disabled = false;
  } else if ((!postformBtn.disabled) && postformMsg.value === "") {
    postformBtn.disabled = true;
  }
})