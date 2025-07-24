document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.querySelector('.my-drawer-toggle-btn');
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            // 在這裡添加您想要執行的操作
            console.log('抽屜切換按鈕被點擊了');
            
            // 例如：切換抽屜的顯示/隱藏
            // const drawer = document.querySelector('.drawer');
            // drawer.classList.toggle('open');
        });
    }
});
