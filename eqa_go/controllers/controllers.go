package controllers

import (
	"eqa_go/repo"
	"github.com/gin-gonic/gin"
	"net/http"
)

func respondWithError(c *gin.Context, code int, message string) {
	c.JSON(code, gin.H{"error": message})
}

func respondWithJSON(c *gin.Context, code int, payload interface{}) {
	c.JSON(code, payload)
}

func respondWithMessage(c *gin.Context, code int, message string) {
	c.JSON(code, gin.H{"message": message})
}

func GetAllMetrics(c *gin.Context) {
	res, err := repo.GetRepo().GetAllKeys()
	if err != nil {
		respondWithError(c, http.StatusInternalServerError, err.Error())
	}
	respondWithJSON(c, http.StatusOK, res)
}

func GetMetric(c *gin.Context) {
	res, err := repo.GetRepo().Get(c.Param("metric"), 3)
	if err != nil {
		respondWithError(c, http.StatusNotFound, "Resource not found")
		return
	}
	respondWithJSON(c, http.StatusOK, res)
}
