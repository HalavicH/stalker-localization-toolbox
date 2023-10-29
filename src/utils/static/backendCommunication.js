import {showNotification} from "./infoProvider.js";


export async function hasNewReport() {
    return await executeGetRequest("/new-report-available");
}

export async function openDiffInVsCode(file1, file2) {
    return await executePostRequest("/diff", {file1, file2});
}

export async function getReportData() {
    const url = "http://127.0.0.1:5000/report";
    return await executeGetRequest("/report");
}


export async function executePostRequest(endpoint, params) {
    const url = "http://127.0.0.1:5000" + endpoint;
    console.log(
        "Executing POST request with:"
        + "\n\turl: " + url
        + "\n\tparams: " + params
    );

    let responseObj = undefined;
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });

        if (!response.ok) {
            showNotification(`<div>Can't execute command.<br>Error: ${data.error}</div>`);
            console.error(response.status);
            responseObj = {error: response.status};
        } else {
            const data = await response.json();

            responseObj = {data};
        }

    } catch (error) {
        console.error("Error calling the endpoint:", error);
        showNotification(`<div>Can't call the server. Error: ${error}</div>`);
        responseObj = {error: error.toString()};
    }

    if (responseObj.error !== undefined) {
        throw Error(responseObj.error);
    }

    return responseObj.data;
}


export async function executeGetRequest(endpoint) {
    const url = "http://127.0.0.1:5000" + endpoint;
    console.log(
        "Executing GET request with:"
        + "\n\turl: " + url
    );

    let responseObj = undefined;

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            showNotification(`<div>Can't get fresh data.<br>Error: ${data.error}</div>`);
            console.error(response.status);
            responseObj = {error: response.status};
        } else {
            const data = await response.json();
            responseObj = {data};
        }

    } catch (error) {
        console.error("Error calling the endpoint:", error);
        showNotification(`<div>Can't call the server. Error: ${error}</div>`);
        responseObj = {error: error.toString()};
    }

    if (responseObj.error !== undefined) {
        throw Error(responseObj.error);
    }

    return responseObj.data;
}