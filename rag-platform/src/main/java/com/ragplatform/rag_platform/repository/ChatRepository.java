package com.ragplatform.rag_platform.repository;

import com.ragplatform.rag_platform.model.Chat;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface ChatRepository extends MongoRepository<Chat, String> {

    List<Chat> findByWorkspaceId(String workspaceId);

}