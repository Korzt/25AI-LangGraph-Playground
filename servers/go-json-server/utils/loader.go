package utils

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"os"

	"go-json-server/models"
)

func LoadProducts(path string) []models.Product {
	file, err := os.Open(path)
	if err != nil {
		log.Fatalf("Failed to open file: %v", err)
	}
	defer file.Close()

	data, err := ioutil.ReadAll(file)
	if err != nil {
		log.Fatalf("Failed to read file: %v", err)
	}

	var products []models.Product
	err = json.Unmarshal(data, &products)
	if err != nil {
		log.Fatalf("Failed to parse JSON: %v", err)
	}

	return products
}
