function autoRefreshPage() {
    console.log('Calling autorefresh...');
    window.location.reload();
}
setInterval(autoRefreshPage, 10000);