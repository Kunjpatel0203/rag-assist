package com.ragplatform.rag_platform.controller;

import com.ragplatform.rag_platform.model.Workspace;
import com.ragplatform.rag_platform.repository.WorkspaceRepository;

import com.ragplatform.rag_platform.service.IngestionService;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/workspace")
public class WorkspaceController {

    private final WorkspaceRepository workspaceRepository;
    private final IngestionService ingestionService;

    public WorkspaceController(WorkspaceRepository workspaceRepository, IngestionService ingestionService) {
        this.workspaceRepository = workspaceRepository;
        this.ingestionService = ingestionService;
    }


    @PostMapping("/create")
    public Workspace createWorkspace(@RequestBody Workspace workspace,
                                     Authentication authentication) {

        String userEmail = authentication.getName();

        workspace.setUserId(userEmail);
        workspace.setCreatedAt(LocalDateTime.now());

        return workspaceRepository.save(workspace);
    }

    @GetMapping("/my")
    public List<Workspace> getMyWorkspaces(Authentication authentication) {

        String userEmail = authentication.getName();

        return workspaceRepository.findByUserId(userEmail);
    }

//    @PostMapping("/{workspaceId}/upload")
//    public String uploadDocument(
//            @PathVariable String workspaceId,
//            @RequestParam("files") MultipartFile[] files
//    ) throws IOException {
//
//        ingestionService.ingestFiles(workspaceId, files);
//
//        return "All files uploaded and ingested successfully.";
//    }
@PostMapping("/{workspaceId}/upload")
public String uploadDocument(
        @PathVariable String workspaceId,
        @RequestParam("files") MultipartFile[] files
) throws IOException {

    ingestionService.ingestFiles(workspaceId, files);

    return "All files uploaded and ingested successfully.";
}
}