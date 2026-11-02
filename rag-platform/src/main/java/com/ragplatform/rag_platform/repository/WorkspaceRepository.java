package com.ragplatform.rag_platform.repository;

import com.ragplatform.rag_platform.model.Workspace;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface WorkspaceRepository extends MongoRepository<Workspace, String> {

    List<Workspace> findByUserId(String userId);
}