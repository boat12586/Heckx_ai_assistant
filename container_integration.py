#!/usr/bin/env python3
"""
Integration with existing Docker containers for Heckx AI
"""

import requests
import json
import os

class ContainerIntegration:
    def __init__(self):
        # Existing container endpoints
        self.services = {
            "kokoro_tts": {
                "name": "Kokoro GPU TTS",
                "url": "http://localhost:8880",
                "container": "kokoro-gpu-tts",
                "features": ["japanese_tts", "gpu_acceleration", "high_quality"],
                "status": "running"
            },
            "nca_toolkit": {
                "name": "No Code Architects Toolkit", 
                "url": "http://localhost:8080",
                "container": "nca-toolkit",
                "features": ["ai_tools", "automation", "workflows"],
                "status": "available"
            },
            "baserow": {
                "name": "Baserow Database",
                "url": "http://localhost:443",
                "url_alt": "http://localhost:85",
                "container": "baserow",
                "features": ["database", "api", "realtime"],
                "status": "available"
            },
            "minio": {
                "name": "MinIO Storage",
                "url": "http://localhost:9000", 
                "container": "miniio",
                "features": ["object_storage", "s3_compatible", "media_storage"],
                "status": "available"
            },
            "n8n": {
                "name": "n8n Automation",
                "url": "http://localhost:5678",
                "container": "n8n", 
                "features": ["workflow_automation", "integrations", "triggers"],
                "status": "available"
            }
        }

    def check_service_health(self, service_name):
        """Check if service is running and healthy"""
        try:
            service = self.services.get(service_name)
            if not service:
                return {"status": "unknown", "error": "Service not found"}
            
            response = requests.get(f"{service['url']}/health", timeout=5)
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": service["url"],
                "container": service["container"]
            }
        except:
            return {"status": "down", "error": "Connection failed"}

    def use_kokoro_tts(self, text, voice="thai_female", speed=1.0):
        """Use Kokoro TTS for voice synthesis"""
        try:
            tts_endpoint = f"{self.services['kokoro_tts']['url']}/synthesize"
            
            payload = {
                "text": text,
                "voice": voice,
                "speed": speed,
                "format": "wav"
            }
            
            response = requests.post(tts_endpoint, json=payload, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "audio_data": response.content,
                    "format": "wav",
                    "service": "kokoro_tts"
                }
            else:
                return {"success": False, "error": f"TTS failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Kokoro TTS error: {str(e)}"}

    def use_nca_toolkit(self, task_type, parameters):
        """Use NCA Toolkit for AI operations"""
        try:
            nca_endpoint = f"{self.services['nca_toolkit']['url']}/api/execute"
            
            payload = {
                "task": task_type,
                "parameters": parameters,
                "output_format": "json"
            }
            
            response = requests.post(nca_endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "result": response.json(),
                    "service": "nca_toolkit"
                }
            else:
                return {"success": False, "error": f"NCA failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"NCA Toolkit error: {str(e)}"}

    def store_in_minio(self, file_data, filename, bucket="heckx-videos"):
        """Store generated content in MinIO"""
        try:
            minio_endpoint = f"{self.services['minio']['url']}/{bucket}/{filename}"
            
            headers = {"Content-Type": "application/octet-stream"}
            response = requests.put(minio_endpoint, data=file_data, headers=headers)
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "url": minio_endpoint,
                    "bucket": bucket,
                    "filename": filename
                }
            else:
                return {"success": False, "error": f"Storage failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"MinIO error: {str(e)}"}

    def save_to_baserow(self, table_id, data):
        """Save video metadata to Baserow database"""
        try:
            baserow_endpoint = f"{self.services['baserow']['url']}/api/database/rows/table/{table_id}/"
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(baserow_endpoint, json=data, headers=headers)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "record_id": response.json().get("id"),
                    "service": "baserow"
                }
            else:
                return {"success": False, "error": f"Database save failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Baserow error: {str(e)}"}

    def trigger_n8n_workflow(self, workflow_id, input_data):
        """Trigger n8n automation workflow"""
        try:
            n8n_endpoint = f"{self.services['n8n']['url']}/webhook/{workflow_id}"
            
            response = requests.post(n8n_endpoint, json=input_data, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "result": response.json(),
                    "service": "n8n"
                }
            else:
                return {"success": False, "error": f"Workflow failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"n8n error: {str(e)}"}

    def create_motivational_video_pipeline(self, quote_data):
        """Complete pipeline using all containers"""
        pipeline_result = {
            "quote": quote_data,
            "steps": [],
            "outputs": {},
            "status": "processing"
        }
        
        # Step 1: Generate voice with Kokoro TTS
        print("🎙️ Generating voice...")
        tts_result = self.use_kokoro_tts(
            text=quote_data["quote"],
            voice="thai_female"
        )
        pipeline_result["steps"].append({"step": "tts", "status": tts_result["success"]})
        
        if tts_result["success"]:
            # Step 2: Store audio in MinIO
            print("💾 Storing audio...")
            audio_filename = f"quote_{quote_data.get('id', 'temp')}_audio.wav"
            storage_result = self.store_in_minio(
                tts_result["audio_data"], 
                audio_filename
            )
            pipeline_result["outputs"]["audio_url"] = storage_result.get("url")
            pipeline_result["steps"].append({"step": "storage", "status": storage_result["success"]})
        
        # Step 3: Use NCA Toolkit for video processing
        print("🎬 Processing with NCA Toolkit...")
        nca_result = self.use_nca_toolkit("video_generation", {
            "quote": quote_data["quote"],
            "theme": quote_data.get("theme", "inspiring"),
            "audio_url": pipeline_result["outputs"].get("audio_url")
        })
        pipeline_result["steps"].append({"step": "nca_processing", "status": nca_result["success"]})
        
        if nca_result["success"]:
            pipeline_result["outputs"]["video_config"] = nca_result["result"]
        
        # Step 4: Save metadata to Baserow
        print("📊 Saving metadata...")
        baserow_data = {
            "quote_text": quote_data["quote"],
            "author": quote_data.get("author", "Unknown"),
            "theme": quote_data.get("theme", "general"),
            "audio_url": pipeline_result["outputs"].get("audio_url"),
            "created_at": "2024-01-01T00:00:00Z",
            "status": "generated"
        }
        
        db_result = self.save_to_baserow("videos", baserow_data)
        pipeline_result["steps"].append({"step": "database", "status": db_result["success"]})
        
        # Step 5: Trigger n8n workflow for post-processing
        print("⚡ Triggering automation...")
        workflow_result = self.trigger_n8n_workflow("video-post-process", {
            "video_id": db_result.get("record_id"),
            "pipeline_data": pipeline_result
        })
        pipeline_result["steps"].append({"step": "automation", "status": workflow_result["success"]})
        
        pipeline_result["status"] = "completed" if all(step["status"] for step in pipeline_result["steps"]) else "partial"
        
        return pipeline_result

    def get_system_status(self):
        """Check status of all containers"""
        status_report = {
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {},
            "overall_health": "unknown"
        }
        
        healthy_count = 0
        total_services = len(self.services)
        
        for service_name, service_info in self.services.items():
            health = self.check_service_health(service_name)
            status_report["services"][service_name] = {
                "name": service_info["name"],
                "health": health["status"],
                "url": service_info["url"],
                "features": service_info["features"]
            }
            
            if health["status"] == "healthy":
                healthy_count += 1
        
        if healthy_count == total_services:
            status_report["overall_health"] = "excellent"
        elif healthy_count >= total_services * 0.7:
            status_report["overall_health"] = "good"
        elif healthy_count >= total_services * 0.5:
            status_report["overall_health"] = "partial"
        else:
            status_report["overall_health"] = "poor"
        
        return status_report

# Test integration
if __name__ == "__main__":
    integration = ContainerIntegration()
    
    # Test system status
    status = integration.get_system_status()
    print("System Status:", json.dumps(status, indent=2))
    
    # Test pipeline
    sample_quote = {
        "id": "test_001",
        "quote": "ความสุขของชีวิตไม่ได้ขึ้นอยู่กับสิ่งที่เกิดขึ้นกับเรา",
        "author": "Epictetus",
        "theme": "resilience"
    }
    
    result = integration.create_motivational_video_pipeline(sample_quote)
    print("Pipeline Result:", json.dumps(result, indent=2, ensure_ascii=False))