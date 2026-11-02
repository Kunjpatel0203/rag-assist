package com.ragplatform.rag_platform.dto;

import lombok.Data;

@Data
public class ApiResponse<T> {

    private boolean success;
    private T data;
    private String error;

    public ApiResponse(boolean success, T data, String error) {
        this.success = success;
        this.data = data;
        this.error = error;
    }

}