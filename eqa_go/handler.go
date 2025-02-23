package main

import (
	"eqa_go/controllers"
	"eqa_go/ext"
	"github.com/gin-gonic/gin"
	"net/http"
)

func Handler(w http.ResponseWriter, r *http.Request) {
	ext.StartUsgs()
	router := gin.Default()
	router.Use(CORSMiddleware())
	controllers.RegisterMetricRoutes(router)
	router.ServeHTTP(w, r)
}

func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	}
}
