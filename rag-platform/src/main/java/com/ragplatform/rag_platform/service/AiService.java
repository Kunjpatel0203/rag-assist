package com.ragplatform.rag_platform.service;

import com.ragplatform.rag_platform.dto.RagRequest;
import com.ragplatform.rag_platform.dto.RagResponse;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class AiService {

    private final RestTemplate restTemplate;

    public AiService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public String askFastAPI(RagRequest ragRequest) {

        String url = "http://127.0.0.1:8000/ask";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<RagRequest> request = new HttpEntity<>(ragRequest, headers);

        System.out.println("Sending request to FastAPI:");
        System.out.println("Workspace: " + ragRequest.getWorkspace_id());
        System.out.println("Question: " + ragRequest.getQuestion());
        System.out.println("History: " + ragRequest.getChatHistory());

        ResponseEntity<RagResponse> response =
                restTemplate.postForEntity(url, request, RagResponse.class);

        if (response.getBody() == null) {
            return "AI response was empty.";
        }

        return response.getBody().getAnswer();
    }
}