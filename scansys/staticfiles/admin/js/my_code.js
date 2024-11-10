function autoRefreshPage() {
    console.log('Calling autorefresh...');
    window.location.reload();
}
setInterval(autoRefreshPage, 1000);