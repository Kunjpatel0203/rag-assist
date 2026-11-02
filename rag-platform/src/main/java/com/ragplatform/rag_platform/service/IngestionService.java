package com.ragplatform.rag_platform.service;

import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import java.io.File;

@Service
public class IngestionService {

    private final RestTemplate restTemplate;

    public IngestionService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public String ingestFiles(String workspaceId, MultipartFile[] files) throws IOException {

        String url = "http://localhost:8000/ingest";

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();

        body.add("workspace_id", workspaceId);

        List<File> tempFiles = new ArrayList<>();

        for (MultipartFile file : files) {

            System.out.println("Uploading file: " + file.getOriginalFilename());

            File tempFile = File.createTempFile("upload_", file.getOriginalFilename());
            file.transferTo(tempFile);

            tempFiles.add(tempFile);

            body.add("files", new FileSystemResource(tempFile));
        }

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        HttpEntity<MultiValueMap<String, Object>> request =
                new HttpEntity<>(body, headers);

        ResponseEntity<String> response =
                restTemplate.postForEntity(url, request, String.class);

        // cleanup temp files
        for (File f : tempFiles) {
            f.delete();
        }

        return response.getBody();
    }
}