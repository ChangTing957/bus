// filepath: [Sample.js](http://_vscodecontentref_/0)

/* 
aaadsdl;al
sglsaga
sfgkjhagl*/
$(function () {
    // 模擬 API 請求
    GetApiResponse();    
});

function GetApiResponse(){    
    $.ajax({
        type: 'GET',
        url: 'https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveTrainDelay?$top=30&$format=JSON',             
        success: function (Data) {
            try {
                $('#apireponse').text(JSON.stringify(Data, null, 2));                
                console.log('Data', Data);
            } catch (e) {
                console.error("Failed to parse response data:", e);
            }
        },
        error: function (xhr, textStatus, thrownError) {
            console.log('errorStatus:', textStatus);
            console.log('Error:', thrownError);
        }
    });
}