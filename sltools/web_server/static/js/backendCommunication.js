import {showError, showNotification} from "./infoProvider.js";


export async function getLastReportHash() {
    return await executeGetRequest("/report-hash");
}

export async function openDiffInVsCode(file1, file2) {
    return await executePostRequest("/diff", {file1, file2});
}

export async function sortEntriesInFiles(file1, file2) {
    return await executePostRequest("/sort-duplicates-only", {file1, file2});
}

export async function getReportData() {
    const url = "http://127.0.0.1:5555/report";
    return await executeGetRequest("/report");
}

export async function executePostRequest(endpoint, params) {
    const url = "http://127.0.0.1:5555" + endpoint;
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
            let error = await getError(response);
            showError(`<div>Can't execute command.<br>Error: ${error}</div>`);
            console.error(response.status);
            responseObj = {error: response.status};
        } else {
            const data = await response.json();

            responseObj = {data};
        }

    } catch (error) {
        console.error("Error calling the endpoint:", error);
        showError(`<div>Can't call the server. Error: ${error}</div>`);
        responseObj = {error: error.toString()};
    }

    if (responseObj.error !== undefined) {
        throw Error(responseObj.error);
    }

    return responseObj.data;
}


async function getError(response) {
    let error = undefined;
    try {
        let data = await response.json();
        return data.error || "Server returned: " + response.statusText;
    } catch (_) {
        return "Server returned: " + response.statusText;
    }
}

export async function executeGetRequest(endpoint) {
    const url = "http://127.0.0.1:5555" + endpoint;
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
            let error = await getError(response);

            showError(`<div>Can't get fresh data.<br>Error: ${error}</div>`);
            console.error(response.status);
            responseObj = {error: response.status};
        } else {
            const data = await response.json();
            responseObj = {data};
        }

    } catch (error) {
        console.error("Error calling the endpoint:", error);
        showError(`<div>Can't call the server. Error: ${error}</div>`);
        responseObj = {error: error.toString()};
    }

    if (responseObj.error !== undefined) {
        throw Error(responseObj.error);
    }

    return responseObj.data;
}