package com.example.icook.data.models

data class User(
    val username: String = "aramirez",
    val name: String = "",
    val lastname: String = "",
    val description: String = "",
    val picture: String = "",
    val password: String = "qwe",
)

data class UserToUpdate(
    val username: String = "",
    val name: String? = null,
    val lastname: String? = null,
    val description: String? = null,
    val picture: String? = null,
    val password: String? = null,
)
