package ext

import (
	"encoding/json"
	"eqa_go/workers"
	"io"
	"log"
	"net/http"
	"net/url"
	"sync"
	"time"

	"eqa_go/model"
)

const USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query?"

var data *model.FeatureCollection
var dataLock sync.Mutex

func getURL(params map[string]string) string {
	// Add default parameters
	params["format"] = "geojson"
	params["minmagnitude"] = "2"

	// Encode query parameters
	query := url.Values{}
	for key, value := range params {
		query.Set(key, value)
	}
	return USGS_URL + query.Encode()
}

func GetData() *model.FeatureCollection {
	if data != nil {
		return data
	}
	dataLock.Lock()
	defer dataLock.Unlock()
	if data != nil {
		return data
	}

	//Collect last 90 days
	endDay := time.Now()
	startDay := endDay.AddDate(0, 0, -90)
	getURL := getURL(map[string]string{"starttime": startDay.Format("02-01-2006")})

	resp, err := http.Get(getURL)
	if err != nil {
		log.Fatalf("Failed to make request: %v", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		log.Fatalf("Request failed with status: %s", resp.Status)
	}
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatalf("Error reading response: %v", err)
	}
	if err := json.Unmarshal(body, &data); err != nil {
		log.Fatalf("Error parsing response: %v", err)
		return nil
	}
	return data
}

func StartUsgs() error {

	eqData := GetData()
	return workers.StartAllWorkers(eqData)
}
