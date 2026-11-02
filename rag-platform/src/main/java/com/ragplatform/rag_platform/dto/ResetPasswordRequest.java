package com.ragplatform.rag_platform.dto;

import lombok.Data;

@Data
public class ResetPasswordRequest {

    private String token;

    private String newPassword;

}